import os
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

QDRANT_URL = os.getenv("QDRANT_DB_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "my_collection")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)


def load_documents(file_path, extension):
    file_path = str(Path(file_path).resolve())
    print("entered load_documents function")

    try:
        if extension == ".pdf":
            result = load_pdf(file_path)
            return result

        return {"status": "skipped", "reason": f"unsupported extension: {extension}"}
    except Exception as e:
        print(f"Error creating directory: {e}")
        return "Failed to load document"


def load_pdf(file_path):
    print(f"Loading PDF from: {file_path}")
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    return chunk_and_store_documents(documents)


def chunk_and_store_documents(documents):
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION_NAME,
    )
    return {"status": "ingested", "chunks": len(chunks)}


if __name__ == "__main__":
    load_documents()
