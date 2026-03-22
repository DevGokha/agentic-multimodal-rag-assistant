from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

DB_PATH = "data/faiss_index"

# Step 0: Check if a FAISS index has been created (i.e. a PDF was uploaded)
def has_faiss_index():
    return os.path.exists(os.path.join(DB_PATH, "index.faiss"))

def process_pdf(file_path):
    # Step 1: Load all pages from the PDF file
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Step 2: Split loaded pages into smaller text chunks
    text_splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = text_splitter.split_documents(documents)

    # Step 3: If no text was extracted, try reading raw page content directly
    # (handles scanned/image-based PDFs that produce empty chunks)
    if not docs:
        raw_texts = [page.page_content.strip() for page in documents if page.page_content.strip()]
        if raw_texts:
            from langchain_core.documents import Document
            docs = [Document(page_content=text) for text in raw_texts]
        else:
            return "No readable text found in the PDF. It may be a scanned/image document."

    # Step 4: Create embeddings from text chunks using HuggingFace model
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Step 5: Build a FAISS vector store from the document chunks and save it
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(DB_PATH)

    return f"PDF processed and stored! ({len(docs)} chunks indexed)"

def query_pdf(query):
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

    docs = db.similarity_search(query, k=3)

    context = "\n".join([doc.page_content for doc in docs])

    return context