import os
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.logging_config import get_logger
from utils.exceptions import ValidationError, ExternalServiceError

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

QDRANT_URL = os.getenv("QDRANT_DB_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "my_collection")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

logger = get_logger("service.data_ingest")


def load_documents(file_path, extension):
    file_path = str(Path(file_path).resolve())
    logger.info("Entered load_documents: %s", file_path)

    try:
        if extension == ".pdf":
            result = load_pdf(file_path)
            return result

        raise ValidationError(f"unsupported extension: {extension}")
    except ValidationError:
        raise
    except Exception as e:
        logger.exception("Error loading document: %s", e)
        raise ExternalServiceError("Failed to load document") from e


def load_pdf(file_path):
    logger.info("Loading PDF from: %s", file_path)
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    return chunk_and_store_documents(documents)


def chunk_and_store_documents(documents):
    try:
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
    except Exception as e:
        logger.exception("Failed to chunk/store documents")
        raise ExternalServiceError("Failed to index documents") from e


if __name__ == "__main__":
    load_documents()
