from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import core components
from app.core.document_processor import DocumentProcessor
from app.core.chunker import DocumentChunker
from app.core.embedder import Embedder
from app.core.reranker import Reranker
from app.core.vector_store import VectorStore

# Import services
from app.services.upload_service import UploadService
from app.services.search_service import SearchService
from app.services.resource_service import ResourceService

# Import routes
from app.api.routes import upload, search, resources

# Import config
from app.config import settings


# Global service instances (initialized on startup)
upload_service: UploadService = None
search_service: SearchService = None
resource_service: ResourceService = None
vector_store: VectorStore = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global upload_service, search_service, resource_service, vector_store

    print("=" * 60)
    print("Initializing SearchMind services...")
    print("=" * 60)

    # Initialize core components
    processor = DocumentProcessor()
    chunker = DocumentChunker()
    embedder = Embedder()
    reranker = Reranker()
    vector_store = VectorStore(
        dimension=settings.EMBEDDING_DIMENSION,
        index_path=settings.INDEX_DIR
    )

    # Initialize services
    upload_service = UploadService(processor, chunker, embedder, vector_store)
    search_service = SearchService(embedder, vector_store, reranker)
    resource_service = ResourceService(vector_store)

    print("=" * 60)
    print(f"SearchMind initialized with {vector_store.get_total_documents()} indexed chunks")
    print("=" * 60)

    yield

    print("Shutting down SearchMind...")


# Create FastAPI application
app = FastAPI(
    title="SearchMind",
    description="Document Search with Vector Retrieval & Re-ranking",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/resources", tags=["upload"])
app.include_router(resources.router, prefix="/resources", tags=["resources"])
app.include_router(search.router, tags=["search"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SearchMind",
        "status": "running",
        "version": "1.0.0",
        "indexed_documents": vector_store.get_total_documents() if search_service else 0
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "upload": upload_service is not None,
            "search": search_service is not None
        },
        "index": {
            "total_chunks": vector_store.get_total_documents() if search_service else 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
