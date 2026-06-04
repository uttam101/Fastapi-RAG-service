import os
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.http.exceptions import UnexpectedResponse

from utils.logging_config import get_logger
from utils.exceptions import ExternalServiceError, ValidationError
from utils.llm_calls import ask_question

QDRANT_URL = os.getenv("QDRANT_DB_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "my_collection")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

logger = get_logger("service.query_data")


def extract_similar_content(query: str):
    if not query or not isinstance(query, str):
        raise ValidationError("Query must be a non-empty string")

    context = ""
    try:
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embedding_model,
            collection_name=QDRANT_COLLECTION_NAME,
            url=QDRANT_URL,
        )

        results = vector_store.similarity_search(query, k=3)

        if not results:
            logger.warning("Query executed, but no relevant documents found.")
            return "No relevant information found for your query."

        for doc in results:
            context += doc.page_content + "\n---\n"

        # generate final answer using LLM helper
        answer = ask_question(context, query)
        return answer

    except UnexpectedResponse as e:
        logger.exception("Qdrant API unexpected response")
        raise ExternalServiceError("Qdrant service error") from e

    except ValueError as e:
        logger.exception("Configuration or input validation error")
        raise ValidationError(str(e)) from e

    except Exception as e:
        logger.exception("Unexpected error during extraction")
        raise ExternalServiceError("Unexpected error during extraction") from e

