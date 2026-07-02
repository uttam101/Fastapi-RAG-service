# Fastapi-RAG-service
FastAPI-based document ingestion and RAG service with PDF ingestion, vector storage, and question-answering over ingested content.

## Current Status
- `GET /health` is available for basic service checks.
- `POST /upload-file` accepts files, validates allowed extensions, deduplicates by content hash, stores uploads under `data/`, and ingests PDFs into Qdrant.
- `POST /ask-question` accepts JSON with a `question` field, performs similarity search against Qdrant, and forwards context to the LLM.
- Global exception handling is implemented with structured `ServiceError` responses.
- File logging is enabled with daily rotation and 7-day retention under `logs/app.log`.

## Tech Stack
- FastAPI
- Uvicorn
- LangChain community loaders and splitters
- Hugging Face embeddings
- Qdrant vector store
- Google Gemini `genai` client

## Quick Start
1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run the API.

```bash
uvicorn main:app --reload
```

4. Check the health endpoint.

```bash
curl http://127.0.0.1:8000/health
```

## API Endpoints
### `GET /health`
Returns service status.

Example response:

```json
{
  "status": "server is Running"
}
```

### `POST /upload-file`
Upload and ingest supported files.

Form field:
- `file`: the uploaded file

Behavior:
- Validates file extension against allowed types.
- Rejects duplicate content by hash.
- Saves the file under `data/<extension>/`.
- Validates write success before ingestion.
- Sends PDFs to the ingestion pipeline.
- Returns `409` for duplicate uploads and `400` for invalid extensions.

### `POST /ask-question`
Ask a question against ingested content.

Request body:

```json
{
  "question": "What is Techdome?"
}
```

Behavior:
- Validates the request schema and ensures the question is non-empty.
- Enforces a maximum question length.
- Performs similarity search in Qdrant.
- Calls the LLM with retrieved context.
- Returns structured errors for validation and external-service failures.

## Error Handling
- Validation errors return `4xx` with a JSON `detail` message.
- External service failures return `502` with a JSON `detail` message.
- Unexpected errors return `500` with a generic `Internal server error` response.
- The application logs both warnings and errors to `logs/app.log`.

## Logging
- Logs are written to stdout and `logs/app.log`.
- `logs/app.log` rotates at midnight.
- Daily retention is configured for 7 days.
- `logs/` is ignored by git in `.gitignore`.

## Project Structure
```
.
├── main.py
├── service/
│   ├── data_ingest.py
│   └── query_data.py
├── utils/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── hash_registry.py
│   ├── llm_calls.py
│   └── logging_config.py
├── data/
│   ├── csv/
│   ├── pdf/
│   └── file_hashes.json
├── logs/
│   └── app.log  # generated at runtime
├── requirements.txt
├── .gitignore
└── README.md
```

## Notes
- Only `.pdf`, `.txt`, and `.csv` uploads are accepted; PDF ingestion is implemented, while text/CSV ingestion is currently not fully supported.
- `ask-question` uses a Pydantic model for request validation and relies on service-layer exception handling.
- Qdrant should be available at `http://localhost:6333`, unless overridden by `QDRANT_DB_URL`.
- The embedding model and collection name can be customized via `EMBEDDING_MODEL_NAME` and `QDRANT_COLLECTION_NAME`.

## Development Roadmap
- Add text and CSV ingestion loaders.
- Add stronger content validation and request size limits.
- Add retries/backoff for Qdrant and LLM calls.
- Add authorization and rate limiting for APIs.
- Add automated tests and CI.

## License
No license specified yet.
