from time import time
from typing import Dict, List, Optional
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.core.reranker import Reranker
from app.models.schemas import SearchResponse, SearchResult, ResultMetadata


class SearchService:
    """Two-stage search: vector search → cross-encoder re-ranking"""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        reranker: Reranker
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker

    async def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: int = 10,
        offset: int = 0,
        limit: int = 10
    ) -> SearchResponse:
        """
        Execute two-stage search pipeline with pagination.

        Stage 1: Vector search with FAISS (fast, retrieve candidates)
        Stage 2: Re-rank with cross-encoder (accurate, return paginated results)

        Args:
            query: Search query
            filters: Optional filters (file_name, type, etc.)
            top_k: Number of candidates to rerank (higher = better quality, slower)
            offset: Number of results to skip
            limit: Number of results to return

        Returns:
            SearchResponse with ranked results
        """
        start_time = time()

        # Calculate how many candidates we need to fetch
        # Fetch enough to cover offset + limit with some buffer
        candidates_needed = max(50, offset + limit + 10)

        # Stage 1: Vector search (get candidates)
        query_embedding = self.embedder.embed_query(query)
        initial_results = self.vector_store.search(query_embedding, k=candidates_needed)

        print(f"Vector search found {len(initial_results)} candidates")

        # Apply filters if provided
        if filters:
            initial_results = self._apply_filters(initial_results, filters)
            print(f"After filtering: {len(initial_results)} candidates")

        # If no results, return empty response
        if not initial_results:
            return SearchResponse(
                query=query,
                results=[],
                total_found=0,
                search_time_ms=(time() - start_time) * 1000,
                has_more=False,
                offset=offset,
                limit=limit
            )

        # Stage 2: Re-rank with cross-encoder
        documents = []
        for metadata, vector_score in initial_results:
            documents.append({
                "text": metadata["text"],
                "metadata": metadata,
                "vector_score": float(vector_score)
            })

        # Rerank more results than needed to ensure quality pagination
        rerank_top_k = min(len(documents), offset + limit + 10)
        reranked = self.reranker.rerank(query, documents, top_k=rerank_top_k)

        # Apply pagination to reranked results
        end_idx = offset + limit
        paginated_results = reranked[offset:end_idx]
        has_more = end_idx < len(reranked)

        # Format results for response
        search_results = []
        for doc in paginated_results:
            search_results.append(SearchResult(
                text=doc["text"],
                metadata=ResultMetadata(
                    file_name=doc["metadata"]["file_name"],
                    page_number=doc["metadata"]["page_number"],
                    resource_id=doc["metadata"]["resource_id"],
                    chunk_id=doc["metadata"]["chunk_id"]
                ),
                rerank_score=doc["rerank_score"],
                vector_score=doc["vector_score"]
            ))

        search_time_ms = (time() - start_time) * 1000

        print(f"Search completed in {search_time_ms:.0f}ms, returned {len(search_results)} results (offset={offset}, has_more={has_more})")

        return SearchResponse(
            query=query,
            results=search_results,
            total_found=len(reranked),
            search_time_ms=search_time_ms,
            has_more=has_more,
            offset=offset,
            limit=limit
        )

    def _apply_filters(
        self,
        results: List[tuple],
        filters: Dict
    ) -> List[tuple]:
        """
        Filter results based on metadata.

        Supported filters:
        - type: File extension (e.g., "pdf", "docx")
        - file_name: Substring match in filename

        Args:
            results: List of (metadata, score) tuples
            filters: Filter criteria

        Returns:
            Filtered list of (metadata, score) tuples
        """
        filtered = []

        for metadata, score in results:
            # Filter by file type
            if "type" in filters:
                ext = metadata["file_name"].split(".")[-1].lower()
                if ext != filters["type"].lower():
                    continue

            # Filter by file name substring
            if "file_name" in filters:
                if filters["file_name"].lower() not in metadata["file_name"].lower():
                    continue

            filtered.append((metadata, score))

        return filtered
