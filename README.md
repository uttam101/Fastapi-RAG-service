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
- Performs similarity search in Qdrant with relevance scoring (see below).
- Calls the LLM with retrieved context.
- Returns structured errors for validation and external-service failures.

#### Similarity Score Threshold

When a question is received, the system does not blindly return the top-k documents. Instead it uses a scored retrieval pipeline:

1. **Embed the query** — the question is converted to a vector using the configured HuggingFace embedding model (`all-MiniLM-L6-v2` by default).
2. **Retrieve top-k with scores** — `similarity_search_with_relevance_scores(query, k=3)` is called against Qdrant. This returns up to 3 `(document, score)` pairs where each score is a cosine similarity in the range `[0.0, 1.0]`. A score of `1.0` means the document is identical to the query; `0.0` means completely unrelated.
3. **Filter by threshold** — every `(doc, score)` pair is checked against `SIMILARITY_THRESHOLD` (default `0.5`):
   - `score >= threshold` → document is included in the context sent to the LLM.
   - `score < threshold` → document is silently dropped.
4. **Guard on empty context** — if all retrieved documents fall below the threshold, the service returns `"No relevant information found for your query."` without calling the LLM at all. The actual top scores are logged as a warning to help with threshold tuning.
5. **LLM call** — only if at least one document passes the filter is the LLM invoked with the filtered context.

This prevents the LLM from hallucinating answers grounded in loosely-related or irrelevant documents.

**Tuning the threshold** — controlled by the `SIMILARITY_THRESHOLD` environment variable:

| Value | Effect |
|-------|--------|
| `0.3` | Very permissive — nearly all results pass; risk of noisy context |
| `0.5` | Default — balanced precision/recall for `all-MiniLM-L6-v2` |
| `0.7` | Strict — only high-confidence matches pass; may return "no relevant info" more often |

Raise the threshold if the LLM is producing vague or off-topic answers. Lower it if the system is too often returning "no relevant information" for questions that should have answers.

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
- The similarity score threshold defaults to `0.5` and can be overridden via `SIMILARITY_THRESHOLD` in `.env`.

## Development Roadmap
- Add text and CSV ingestion loaders.
- Add stronger content validation and request size limits.
- Add retries/backoff for Qdrant and LLM calls.
- Add authorization and rate limiting for APIs.
- Add automated tests and CI.

## License
No license specified yet.
