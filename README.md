# SearchMind: Document Search with Vector Retrieval & Re-ranking

A production-ready document search system using FAISS vector search and cross-encoder re-ranking. Upload PDF/DOCX documents and search them with semantic understanding.

## Features

- **Document Upload**: PDF and DOCX support with OCR for scanned documents
- **Smart Chunking**: Token-based text splitting with overlap for context preservation
- **Two-Stage Search**:
  - Stage 1: Fast FAISS vector search (top 25 candidates)
  - Stage 2: Accurate cross-encoder re-ranking (top 10 results)
- **Multilingual Support**: Using paraphrase-multilingual-MiniLM-L12-v2
- **Modern UI**: React + TypeScript with clean, responsive design

## Architecture

```
React Frontend (Upload + Search Pages)
        ↓
FastAPI Backend
        ↓
Processing Pipeline: Upload → OCR → Chunk → Embed → FAISS Index
        ↓
Search Pipeline: Query → Vector Search (top 25) → Re-rank (top 10)
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- 2GB+ free disk space (for ML models)

### With Docker (Recommended)

```bash
# Build and start all services
make build
make up

# View logs
make logs

# Stop services
make down
```

Services will be available at:
- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:5173`

Run `make help` for all available commands.

### Local Development

#### Backend Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Models will auto-download on first run (~500MB)

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Usage

1. **Upload Documents**
   - Navigate to Upload page
   - Drag & drop or select PDF/DOCX files (max 50MB)
   - Wait for processing (text extraction + indexing)

2. **Search Documents**
   - Navigate to Search page
   - Enter query and press Search
   - View ranked results with relevance scores

## API Endpoints

### Upload Document
```bash
POST /resources/upload
Content-Type: multipart/form-data

Response:
{
  "resource_id": "uuid",
  "filename": "document.pdf",
  "num_chunks": 45,
  "status": "success"
}
```

### Search Documents
```bash
POST /search
Content-Type: application/json

{
  "query": "contract duration",
  "top_k": 10,
  "filters": {
    "type": "pdf",
    "file_name": "contract"
  }
}

Response:
{
  "query": "contract duration",
  "results": [
    {
      "text": "Full text snippet...",
      "metadata": {
        "file_name": "contract.pdf",
        "page_number": 5,
        "resource_id": "uuid",
        "chunk_id": "uuid"
      },
      "rerank_score": 0.9123,
      "vector_score": 0.8456
    }
  ],
  "total_found": 25,
  "search_time_ms": 150
}
```

## Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **FAISS**: Facebook AI Similarity Search for vector indexing
- **sentence-transformers**: Embedding and re-ranking models
- **PaddleOCR**: Advanced OCR for scanned documents
- **LangChain**: Text splitting utilities

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool
- **React Router**: Client-side routing
- **Axios**: HTTP client

### Models
- **Embeddings**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
- **Re-ranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

## Performance

- **OCR**: ~2-5s per scanned page
- **Embedding**: ~100ms for 32 chunks (CPU)
- **Search**: ~150-300ms end-to-end (including re-ranking)
- **Index size**: ~1.5KB per chunk

## Project Structure

```
searchmind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Core components (OCR, embeddings, vector store)
│   │   ├── services/            # Business logic
│   │   └── models/              # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client
│   │   └── hooks/               # Custom React hooks
│   └── package.json
└── data/                        # Data storage
    ├── uploads/                 # Uploaded files
    ├── faiss_index/             # Vector index + metadata
    └── temp/                    # Temporary files
```

## Development

### Run Backend Tests
```bash
cd backend
pytest
```

### Run Frontend Dev Server
```bash
cd frontend
npm run dev
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

## Configuration

### Backend (.env)
```
DATA_DIR=./data
CHUNK_SIZE=400
CHUNK_OVERLAP=80
MAX_FILE_SIZE_MB=50
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### PaddleOCR Installation Issues
```bash
# macOS
brew install poppler

# Ubuntu/Debian
apt-get install poppler-utils

# Windows
# Download poppler from https://github.com/oschwartz10612/poppler-windows
```

### Model Download Fails
Models auto-download on first run. If download fails:
```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
  SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'); \
  CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
```

### FAISS Index Corruption
```bash
# Delete and rebuild index
rm -rf data/faiss_index/*
# Re-upload documents
```

## Limitations

- No authentication/authorization (MVP)
- No document deletion from index
- No multi-tenancy support
- Local filesystem storage only

## License

MIT

## Credits

- FAISS by Facebook AI Research
- sentence-transformers by UKPLab
- PaddleOCR by PaddlePaddle
