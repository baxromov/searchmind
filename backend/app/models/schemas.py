from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)


class ResultMetadata(BaseModel):
    """Metadata for each search result"""
    file_name: str
    page_number: int
    resource_id: str
    chunk_id: str


class SearchResult(BaseModel):
    """Individual search result with full details"""
    text: str  # Full text snippet (400 tokens)
    metadata: ResultMetadata  # File info
    rerank_score: float  # Cross-encoder score
    vector_score: float  # FAISS similarity score


class SearchResponse(BaseModel):
    """Complete search response"""
    query: str
    results: List[SearchResult]
    total_found: int  # Total candidates before re-ranking
    search_time_ms: float
    has_more: bool  # Whether there are more results available
    offset: int  # Current offset
    limit: int  # Current limit


class UploadResponse(BaseModel):
    resource_id: str
    filename: str
    num_chunks: int
    status: str


class PageContent(BaseModel):
    """Represents a single page of a document"""
    text: str
    page_num: int


class Chunk(BaseModel):
    """Represents a text chunk with metadata"""
    text: str
    page: int
    resource_id: str
    file_name: str


class Resource(BaseModel):
    """Resource metadata for uploaded documents"""
    resource_id: str
    filename: str
    num_chunks: int
    uploaded_at: str


class ChunkDetail(BaseModel):
    """Detailed chunk information"""
    chunk_id: str
    text: str
    page_number: int


class ChatMessage(BaseModel):
    """Chat message with role and content"""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000)
    history: Optional[List[ChatMessage]] = []


class Source(BaseModel):
    """Source document for chat response"""
    file_name: str
    page_number: int
    text: str
    score: float


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    answer: str
    sources: List[Source]
    rewritten_query: str
    search_time_ms: float
