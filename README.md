# Fastapi-RAG-service
FastAPI-based document ingestion and RAG service with PDF ingestion, vector storage, and question-answering over ingested content.

## Current Status
- `GET /health` is available for basic service checks.
- `POST /upload-file` accepts files, validates allowed extensions, deduplicates by content hash, stores uploads under `data/`, and ingests PDFs into Qdrant.
- `POST /ask-question` accepts JSON with a `question` field, performs similarity search against Qdrant, and forwards context to the LLM.
- Global exception handling is implemented with structured `ServiceError` responses.
- File logging is enabled with daily rotation and 7-day retention under `logs/app.log`.

## Tech Stack
- **FastAPI** — exposes the health, upload, and question-answering APIs with request validation.
- **Uvicorn** — runs the ASGI application locally.
- **PyMuPDF** — extracts text and page metadata from PDF files.
- **LangChain text splitters** — turns extracted documents into overlapping chunks.
- **Hugging Face Sentence Transformers** — converts both documents and queries into vectors.
- **Qdrant** — stores document vectors and performs nearest-neighbor similarity search.
- **Google Gemini** — generates the final answer from the retrieved context.
- **python-dotenv** — loads local environment configuration from `.env`.

### Why these components?

- FastAPI and Uvicorn are a small, production-oriented HTTP layer for Python services.
- PyMuPDF is used because this service currently ingests PDFs and needs their text and page metadata.
- LangChain provides the document and splitter interfaces used by the ingestion pipeline without requiring a custom chunking implementation.
- `sentence-transformers/all-MiniLM-L6-v2` is the default embedding model because it is relatively small and fast while providing useful general-purpose semantic search. Larger embedding models may improve retrieval quality but require more memory and compute.
- Qdrant is a dedicated vector database that persists embeddings and supports efficient similarity search, instead of requiring all vectors to be loaded into application memory.
- Gemini is used as the answer-generation model. The application sends it only retrieved context and instructs it to answer using that context.

The model choices are defaults, not guarantees that they are optimal for every dataset. Embedding models should be evaluated with representative questions and documents before changing them, because vectors produced by different embedding models are not interchangeable within one collection.

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

## How the RAG Pipeline Works

### Document ingestion

1. A client uploads a file to `POST /upload-file`.
2. The API validates the extension, calculates a content hash, rejects duplicate content or filenames, and saves the file under `data/pdf/` for PDF uploads.
3. `PyMuPDFLoader` extracts the PDF into LangChain `Document` objects. Each document retains text and source metadata such as the page number.
4. `RecursiveCharacterTextSplitter` divides the extracted text into chunks of up to 1,000 characters with 200 characters of overlap. The overlap helps preserve meaning when an answer spans a chunk boundary.
5. `HuggingFaceEmbeddings` converts every chunk into a numeric vector using `EMBEDDING_MODEL_NAME`.
6. Qdrant stores the chunk text, metadata, and vector in `QDRANT_COLLECTION_NAME`. The vector is what enables semantic search later; the original chunk text is what is supplied to the LLM.

Only PDF ingestion is implemented in the current service. `.txt` and `.csv` are accepted by the upload validation list, but `load_documents` currently raises an unsupported-extension error for them.

### Question answering

1. The API validates the question and creates a query embedding with the same embedding model used for document chunks.
2. Qdrant compares the query vector with stored chunk vectors and returns the three nearest chunks with relevance scores.
3. The application removes results below `SIMILARITY_THRESHOLD`.
4. The surviving chunk text is joined into a context string.
5. Gemini receives the context and question and is instructed to answer using only that context.

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

The current query pipeline is a single-stage vector retrieval pipeline:

1. **Validate the question** — `/ask-question` trims the input, rejects empty questions, and limits the length to 1,000 characters.
2. **Embed the query** — `HuggingFaceEmbeddings` uses `EMBEDDING_MODEL_NAME` to convert the question into a vector in the same embedding space used during ingestion.
3. **Retrieve candidates** — Qdrant searches the collection using `similarity_search_with_relevance_scores(query, k=3)`. It returns up to three `(document, score)` pairs, ordered from most to least similar according to the collection's configured distance metric.
4. **Filter by threshold** — every result is checked against `SIMILARITY_THRESHOLD` (default `0.5`):
   - `score >= threshold` → document is included in the context sent to the LLM.
   - `score < threshold` → document is silently dropped.
5. **Guard on empty context** — if no result passes the threshold, the service returns `"No relevant information found for your query."` without calling Gemini. The retrieved scores are logged for threshold tuning.
6. **Generate the answer** — the remaining chunk text is joined into a context string and sent to Gemini with the question.

This prevents the LLM from hallucinating answers grounded in loosely-related or irrelevant documents.

The score is a relevance value produced by LangChain's Qdrant integration. Its exact scale and interpretation depend on the Qdrant distance metric and the integration's relevance-score conversion; it should not be assumed to be a universal probability or a guaranteed `[0, 1]` cosine score. Tune the threshold using real retrieval examples from this collection.

**Tuning the threshold** — controlled by the `SIMILARITY_THRESHOLD` environment variable:

| Value | Effect |
|-------|--------|
| `0.3` | Very permissive — nearly all results pass; risk of noisy context |
| `0.5` | Default — balanced precision/recall for `all-MiniLM-L6-v2` |
| `0.7` | Strict — only high-confidence matches pass; may return "no relevant info" more often |

Raise the threshold if the LLM is producing vague or off-topic answers. Lower it if the system is too often returning "no relevant information" for questions that should have answers.

### Current limitations

- `k=3` is fixed in `service/query_data.py`, so chunks ranked below the first three are never considered.
- There is currently no second-stage cross-encoder re-ranking. Increasing `k` alone retrieves more candidates, but does not add a separate semantic re-ranking model.
- The LLM context is limited indirectly by returning at most three threshold-passing chunks; there is no token-budget calculation yet.

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
- The Gemini client reads `GEMINI_API_KEY` from the environment.
- Qdrant, the embedding model, and Gemini are external/runtime dependencies; the API will not be fully usable until Qdrant is running, the embedding model can be loaded, and `GEMINI_API_KEY` is configured.

## Development Roadmap
- Add text and CSV ingestion loaders.
- Add stronger content validation and request size limits.
- Add retries/backoff for Qdrant and LLM calls.
- Add authorization and rate limiting for APIs.
- Add automated tests and CI.

## License
No license specified yet.
