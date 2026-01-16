import os
import re
import sys
import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

print("=== APP STARTING (Lightweight Version) ===", flush=True)

app = Flask(__name__)
CORS(app)

# Global variables - NO vector store needed!
llm = None
all_chunks = []
chunk_texts = []  # Simple list of text for keyword search

CUSTOM_PROMPT = """You are an expert legal assistant specializing in the Indian Penal Code 1860.
Use ONLY the following context from the IPC document to answer the question.
If a specific section is mentioned, quote the exact text.

Context from IPC Document:
{context}

Question: {question}

Provide a clear, accurate answer based on the context above:"""

def initialize_chatbot():
    global llm, all_chunks, chunk_texts
    
    if llm is not None:
        return

    try:
        print("Starting lightweight initialization...", flush=True)
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("ERROR: GROQ_API_KEY not set!", flush=True)
            return
        print("GROQ_API_KEY found", flush=True)
        
        pdf_path = "THE-INDIAN-PENAL-CODE-1860.pdf"
        if not os.path.exists(pdf_path):
            print(f"ERROR: PDF not found at {pdf_path}", flush=True)
            print(f"Files: {os.listdir('.')}", flush=True)
            return
        
        print(f"Loading PDF...", flush=True)
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Loaded {len(docs)} pages", flush=True)

        # Larger chunks for memory efficiency
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )
        all_chunks = splitter.split_documents(docs)
        chunk_texts = [chunk.page_content.lower() for chunk in all_chunks]
        print(f"Created {len(all_chunks)} chunks", flush=True)

        # Initialize only Groq LLM - no local embeddings!
        print("Initializing Groq LLM...", flush=True)
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        print("Chatbot initialized successfully!", flush=True)
        
    except Exception as e:
        print(f"ERROR: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()

def keyword_search(query, top_k=8):
    """Simple keyword-based search - no embeddings needed!"""
    query_lower = query.lower()
    scores = []
    
    # Extract section numbers from query
    section_nums = re.findall(r'\b(\d{1,3}[A-Z]?)\b', query)
    
    # Keywords from query
    keywords = set(re.findall(r'\b\w{3,}\b', query_lower))
    
    for i, text in enumerate(chunk_texts):
        score = 0
        
        # Boost for section number matches
        for num in section_nums:
            patterns = [f"section {num}", f"sec. {num}", f"{num}.", f"[{num}]"]
            if any(p in text for p in patterns):
                score += 100
        
        # Score for keyword matches
        for keyword in keywords:
            if keyword in text:
                score += text.count(keyword) * 2
        
        # Boost for common legal terms
        legal_terms = ['punishment', 'offence', 'imprisonment', 'fine', 'whoever', 'shall be']
        for term in legal_terms:
            if term in query_lower and term in text:
                score += 10
        
        scores.append((score, i))
    
    # Sort by score and get top results
    scores.sort(reverse=True)
    top_indices = [idx for score, idx in scores[:top_k] if score > 0]
    
    # If no matches, return first few chunks as fallback
    if not top_indices:
        top_indices = list(range(min(5, len(all_chunks))))
    
    return [all_chunks[i] for i in top_indices]

@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "name": "IPC Chatbot API (Lightweight)",
        "initialized": llm is not None,
        "chunks": len(all_chunks)
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "initialized": llm is not None})

@app.route("/chat", methods=["POST"])
def chat():
    return ask()

@app.route("/ask", methods=["POST"])
def ask():
    if llm is None:
        return jsonify({"error": "Chatbot not initialized"}), 500

    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Use keyword search instead of embeddings
        relevant_docs = keyword_search(query)
        context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
        
        full_prompt = CUSTOM_PROMPT.format(context=context, question=query)
        response = llm.invoke(full_prompt)
        
        return jsonify({"answer": response.content})

    except Exception as e:
        print(f"Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

# Initialize on module load
print("=== INITIALIZING ===", flush=True)
initialize_chatbot()
print("=== READY ===", flush=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
