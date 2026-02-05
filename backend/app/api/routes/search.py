from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse


router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search indexed documents using two-stage retrieval:

    Stage 1: Vector search with FAISS (fast, top 25 candidates)
    Stage 2: Re-rank with cross-encoder (accurate, top K results)

    Args:
        request: SearchRequest with query, filters, and top_k

    Returns:
        SearchResponse with ranked results
    """
    # Service will be injected via dependency
    from app.main import search_service

    try:
        result = await search_service.search(
            query=request.query,
            filters=request.filters,
            top_k=request.top_k,
            offset=request.offset,
            limit=request.limit
        )
        return result
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
