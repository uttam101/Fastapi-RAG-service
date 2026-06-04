import os
import logging
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.http.exceptions import UnexpectedResponse
from utils.llm_calls import ask_question

QDRANT_URL = os.getenv("QDRANT_DB_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "my_collection")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

# Setup logger to track issues gracefully
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QdrantExtraction")
def extract_similar_content(query):
    context = ""
    try:
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embedding_model,
            collection_name=QDRANT_COLLECTION_NAME,
            url=QDRANT_URL,
            # api_key="your-api-key"         
        )
        query = "what is Techdome?"
        results = vector_store.similarity_search(query, k=3)

        if not results:
                logger.warning("Query executed, but no relevant documents found.")
                return "No relevant information found for your query."
        else:
            for doc in results:
                context += doc.page_content + "\n---\n"
            answer = ask_question(context, query)
            return answer
        
            


    except UnexpectedResponse as e:
        logger.error(f"Qdrant API error: Status {e.status_code} - {e.reason_phrase}")

    except ValueError as e:
        # Catches bad query parameters, wrong types, or connection strings
        logger.error(f"Configuration or input validation error: {e}")

    except Exception as e:
        # Catch-all for network losses, drops, timeouts, or unexpected system issues
        logger.error(f"An unexpected error occurred during extraction: {e}")

