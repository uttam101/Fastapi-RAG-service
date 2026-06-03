from langchain_community.document_loaders import PyMuPDFLoader
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import os

def load_documents(file_path, extension):
    print("entered load_documents function")
    try:
        if extension == ".pdf":
            return load_pdf(file_path)
    except Exception as e:
        print(f"Error creating directory: {e}")
        return "Failed to load document"

def load_pdf(file_path):
    print(f"Loading PDF from: {file_path}")
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    chunk_and_store_documents(documents)

def chunk_and_store_documents(documents):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url="http://localhost:6333",
        collection_name="my_collection",
    )
    return

if __name__ == "__main__":
    load_documents()
