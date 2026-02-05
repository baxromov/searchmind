# SearchMind Backend

FastAPI backend with FAISS vector search and cross-encoder re-ranking.

## Setup with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

### Quick Start

```bash
# Install dependencies (uv will create .venv automatically)
uv pip install -e .

# Or use sync (recommended)
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run server
uvicorn app.main:app --reload --port 8000
```

### Development

```bash
# Install dev dependencies
uv pip install -e .[dev]

# Run tests
pytest

# Add new dependency
uv pip install <package>
# Then add to pyproject.toml
```

## API Endpoints

### Upload Document
```bash
POST /resources/upload
Content-Type: multipart/form-data

curl -X POST http://localhost:8000/resources/upload \
  -F "file=@document.pdf"
```

### Search Documents
```bash
POST /search
Content-Type: application/json

curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "contract duration", "top_k": 10}'
```

### Health Check
```bash
GET /health

curl http://localhost:8000/health
```

## Configuration

Edit `.env` file:

```env
DATA_DIR=./data
UPLOAD_DIR=./data/uploads
INDEX_DIR=./data/faiss_index
TEMP_DIR=./data/temp

CHUNK_SIZE=400
CHUNK_OVERLAP=80
MAX_FILE_SIZE_MB=50
```

## Architecture

```
FastAPI App
    ↓
Services (Upload, Search)
    ↓
Core Components:
    - DocumentProcessor (PDF/DOCX + OCR)
    - Chunker (Token-based splitting)
    - Embedder (Multilingual embeddings)
    - VectorStore (FAISS + metadata)
    - Reranker (Cross-encoder)
```

## Models

- **Embeddings**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dim)
- **Re-ranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

Models auto-download on first run (~500MB total).
