# Fastapi-RAG-service
Early-stage FastAPI service scaffold for a Retrieval-Augmented Generation (RAG) API. This repository currently exposes a single health endpoint and is prepared for future RAG capabilities.

## Status
- Current: minimal FastAPI app with `/health`.
- Planned: document ingestion, chunking, embeddings, vector search, and LLM-powered QA.

## Highlights
- FastAPI app scaffold with OpenAPI docs.
- Health endpoint for uptime checks.

## Tech Stack
- FastAPI
- Uvicorn
- Python 3.10+ (3.12 used in development)

## Quick Start
1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the server

```bash
uvicorn main:app --reload
```

4. Verify health

```bash
curl http://127.0.0.1:8000/health
```

## API
### GET /health
Returns a simple service status response.

Example response:

```json
{
	"status:": "server is Running"
}
```

## Project Structure
```
.
├── main.py
├── requirements.txt
└── README.md
```

## Roadmap
- Document ingestion and storage
- Chunking and embedding generation
- Vector database integration
- Retrieval pipeline
- LLM answer synthesis
- Tests and CI

## Contributing
Issues and pull requests are welcome. Please keep changes small and focused until core features land.

## License
No license specified yet.
