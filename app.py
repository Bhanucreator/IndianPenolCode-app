import os
import re
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

    # Load IPC PDF
    loader = PyPDFLoader("THE-INDIAN-PENAL-CODE-1860.pdf")
    docs = loader.load()
    print(f"Loaded {len(docs)} pages from PDF")

    # Document Splitting - Smaller chunks for better precision
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    all_chunks = splitter.split_documents(docs)
    print(f"Created {len(all_chunks)} chunks")

    # Create embeddings and vector store
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(all_chunks, embedding)

    # Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )
    
    print("Chatbot initialized successfully!")

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
            "/ask": "POST - Send a query about IPC"
        }
    })

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
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    initialize_chatbot()
    app.run(host='0.0.0.0', port=5000, debug=True)
