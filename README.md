# Fastapi-RAG-service
FastAPI-based document ingestion service for a Retrieval-Augmented Generation (RAG) pipeline. The current stage supports file upload, local persistence, PDF loading, chunking, Qdrant storage for embeddings, and hash-based deduplication to prevent duplicate embeddings.

## Current Status
- `GET /health` is available for basic service checks.
- `POST /upload-file` accepts uploads, validates the extension, saves the file under `data/`, and forwards PDFs into the ingestion pipeline.
- `script/data_ingest.py` currently handles PDF loading, document chunking, and vector store creation.
- `utils/hash_registry.py` handles upload hashing, duplicate detection, and registry updates.
- The RAG answer-generation API is not implemented yet.

## Tech Stack
- FastAPI
- Uvicorn
- LangChain community loaders and splitters
- Hugging Face embeddings
- Qdrant vector store

## Quick Start
1. Create and activate a virtual environment.

```bash
python -m venv .venv
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
Basic service status response.

Example response:

```json
{
  "status": "server is Running"
}
```

### `POST /upload-file`
Uploads a file, stores it locally, and starts ingestion for supported PDFs.

Form field:
- `file`: uploaded file

Current behavior:
- Validates the file extension against the allowed list.
- Saves the file into a type-based subdirectory under `data/`.
- Calls `load_documents(file_path, extension)` after a successful save.

### Deduplication behavior
- Uploaded PDF content is hashed before ingestion.
- Previously ingested files are tracked in `data/file_hashes.json`.
- If the same file content is uploaded again, ingestion is skipped and duplicate embeddings are not created.

## Ingestion Flow
1. Receive the uploaded file in `main.py`.
2. Persist it on disk under `data/<extension>/`.
3. Pass the saved path to `script/data_ingest.py`.
4. Load the document with `PyMuPDFLoader` for PDFs.
5. Split the document into chunks.
6. Store the chunks in Qdrant using `sentence-transformers/all-MiniLM-L6-v2` embeddings.
7. Save the file hash so future uploads of the same content are skipped.

## Project Structure
```
.
├── main.py
├── script/
│   └── data_ingest.py
├── utils/
│   ├── __init__.py
│   └── hash_registry.py
├── data/
│   └── file_hashes.json
├── requirements.txt
└── README.md
```

## Notes
- The ingestion path currently processes PDFs only in `load_documents`.
- `text/plain` and `text/csv` are accepted by the upload endpoint, but their downstream loaders are not implemented yet.
- Qdrant must be running at `http://localhost:6333` for vector storage to work, unless overridden with `QDRANT_DB_URL`.
- You can override the collection name and embedding model with `QDRANT_COLLECTION_NAME` and `EMBEDDING_MODEL_NAME`.
- Duplicate detection lives in `utils/hash_registry.py` so ingestion code stays focused on document processing.

## Development Roadmap
- Add loaders for text and CSV files.
- Add MIME/content validation.
- Add error handling and structured API responses.
- Add retrieval and answer-generation endpoints.
- Add tests and CI.

## License
No license specified yet.
