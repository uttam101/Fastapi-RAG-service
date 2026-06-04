from google import genai
from google.genai import types, errors
import os

from utils.logging_config import get_logger
from utils.exceptions import ExternalServiceError

logger = get_logger("utils.llm_calls")


def ask_question(context, question):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}"

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=300,
                system_instruction="You are a helpful assistant. Answer the query using ONLY the provided context snippets."
            )
        )
        return response.text

    except errors.ClientError as e:
        logger.exception("LLM client error: %s", e)
        raise ExternalServiceError("LLM client error") from e

    except errors.ServerError as e:
        logger.exception("LLM server error: %s", e)
        raise ExternalServiceError("LLM server error") from e

    except errors.APIError as e:
        logger.exception("LLM API error: %s", e)
        raise ExternalServiceError("LLM API error") from e

    except Exception as e:
        logger.exception("Unexpected system error in LLM call: %s", e)
        raise ExternalServiceError("Unexpected LLM error") from e
