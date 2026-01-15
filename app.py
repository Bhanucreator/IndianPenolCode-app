import os
import re
import sys
import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

# Force unbuffered output for Render logs
print("=== APP STARTING ===", flush=True)

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app requests

# Global variables
vectorstore = None
llm = None
all_chunks = []

# Custom prompt for better answers
CUSTOM_PROMPT = """You are an expert legal assistant specializing in the Indian Penal Code 1860. 
Use ONLY the following context from the IPC document to answer the question.
Quote the exact text from the sections when available.
If the information is in the context, provide a complete answer.

Context from IPC Document:
{context}

Question: {question}

Answer based strictly on the above context:"""

def initialize_chatbot():
    global vectorstore, llm, all_chunks
    
    if vectorstore is not None:
        return

    try:
        print("Starting chatbot initialization...", flush=True)
        sys.stdout.flush()
        
        # Check for GROQ API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY environment variable not set!", flush=True)
            return
        print("GROQ_API_KEY found", flush=True)
        
        # Find PDF file
        pdf_path = "THE-INDIAN-PENAL-CODE-1860.pdf"
        print(f"Looking for PDF at: {pdf_path}", flush=True)
        print(f"Current directory: {os.getcwd()}", flush=True)
        print(f"Files in directory: {os.listdir('.')}", flush=True)
        
        if not os.path.exists(pdf_path):
            # Try alternative paths
            alt_paths = [
                os.path.join(os.path.dirname(__file__), "THE-INDIAN-PENAL-CODE-1860.pdf"),
                "/app/THE-INDIAN-PENAL-CODE-1860.pdf",
            ]
            for alt in alt_paths:
                print(f"Trying: {alt}", flush=True)
                if os.path.exists(alt):
                    pdf_path = alt
                    break
        
        if not os.path.exists(pdf_path):
            print(f"ERROR: PDF file not found!", flush=True)
            return
        
        print(f"Loading PDF from: {pdf_path}", flush=True)
        
        # Load IPC PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} pages from PDF", flush=True)

        # Document Splitting - LARGER chunks to reduce memory usage on Render free tier
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # Larger chunks = fewer total chunks
            chunk_overlap=100,  # Less overlap
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        all_chunks = splitter.split_documents(docs)
        print(f"Created {len(all_chunks)} chunks", flush=True)

        # Create embeddings - use batches to reduce memory
        print("Creating embeddings (optimized for low memory)...", flush=True)
        
        # Use smaller model and batch processing
        embedding = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'batch_size': 32, 'normalize_embeddings': True}
        )
        
        # Create vector store in batches to save memory
        batch_size = 50
        vectorstore = None
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(all_chunks)-1)//batch_size + 1}...", flush=True)
            if vectorstore is None:
                vectorstore = FAISS.from_documents(batch, embedding)
            else:
                batch_vectorstore = FAISS.from_documents(batch, embedding)
                vectorstore.merge_from(batch_vectorstore)
        
        print("Vector store created", flush=True)

        # Initialize Groq LLM
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        print("Chatbot initialized successfully!", flush=True)
        
    except Exception as e:
        print(f"ERROR during initialization: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

def search_by_section_number(query):
    """Search for specific section numbers in the chunks"""
    # Extract section numbers from query (e.g., "302", "420", "376")
    section_pattern = r'\b(\d{1,3}[A-Z]?)\b'
    matches = re.findall(section_pattern, query)
    
    relevant_chunks = []
    for chunk in all_chunks:
        chunk_text = chunk.page_content.lower()
        for section_num in matches:
            # Look for patterns like "Section 302", "302.", "S. 302"
            patterns = [
                f"section {section_num}".lower(),
                f"sec. {section_num}".lower(),
                f"s. {section_num}".lower(),
                f"{section_num}.",
                f"[{section_num}]",
            ]
            if any(p in chunk_text for p in patterns):
                relevant_chunks.append(chunk)
                break
    
    return relevant_chunks

def get_relevant_context(query):
    """Get relevant context using hybrid search"""
    # First, try to find by section number
    section_chunks = search_by_section_number(query)
    
    # Also do semantic search
    semantic_results = vectorstore.similarity_search(query, k=8)
    
    # Combine results, prioritizing section matches
    all_results = section_chunks + [doc for doc in semantic_results if doc not in section_chunks]
    
    # Limit to top 10 most relevant
    return all_results[:10]

@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "name": "IPC Chatbot API",
        "endpoints": {
            "/ask": "POST - Send a query about IPC",
            "/health": "GET - Health check"
        }
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "chatbot": vectorstore is not None})

@app.route("/chat", methods=["POST"])
def chat():
    """Alias for /ask endpoint"""
    return ask()

@app.route("/ask", methods=["POST"])
def ask():
    global vectorstore, llm
    if vectorstore is None or llm is None:
        return jsonify({"error": "Chatbot not initialized"}), 500

    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Get relevant context using hybrid search
        relevant_docs = get_relevant_context(query)
        
        # Combine context
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Build the prompt
        full_prompt = CUSTOM_PROMPT.format(context=context, question=query)
        
        # Get response from LLM
        response = llm.invoke(full_prompt)
        answer = response.content
        
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

# Initialize chatbot when module loads (for gunicorn)
print("=== CALLING INITIALIZE_CHATBOT ===", flush=True)
initialize_chatbot()
print("=== INITIALIZATION COMPLETE ===", flush=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
