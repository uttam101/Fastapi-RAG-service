from google import genai
from google.genai import types, errors
import os


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
        print(f" Client Error (Fix your request/setup): Status Code {e.code} - {e.message}")
        return "Sorry, there was an issue processing your request. Please check your input and try again."
    
    except errors.ServerError as e:
        print(f" Server Error (Google side is down): Status Code {e.code} - {e.message}")
        return "Sorry, there was a server error. Please try again later."

    except errors.APIError as e:
        print(f" API Error: {e}")
        return "Sorry, there was an API error. Please try again later."

    except Exception as e:
        print(f" Unexpected system error occurred: {e}")
        return "Sorry, an unexpected error occurred. Please try again later."
