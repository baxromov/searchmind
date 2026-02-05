from sentence_transformers import CrossEncoder
from typing import List, Dict
from app.config import settings


class Reranker:
    """Re-rank search results using cross-encoder"""

    def __init__(self):
        self.model = CrossEncoder(settings.RERANKER_MODEL)
        print(f"Loaded re-ranker model: {settings.RERANKER_MODEL}")

    def rerank(self, query: str, documents: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        Re-rank documents using cross-encoder.

        Args:
            query: Search query
            documents: List of dicts with 'text', 'metadata', 'vector_score'
            top_k: Number of top results to return

        Returns:
            List of documents sorted by rerank_score (highest first)
        """
        if not documents:
            return []

        # Create query-document pairs
        pairs = [(query, doc["text"]) for doc in documents]

        # Get relevance scores (logits from cross-encoder)
        scores = self.model.predict(pairs)

        # Normalize scores to 0-1 range using min-max normalization
        # This ensures scores are always between 0-1 for display as percentages
        min_score = float(scores.min())
        max_score = float(scores.max())
        score_range = max_score - min_score

        # Add normalized rerank scores to documents
        for doc, score in zip(documents, scores):
            # Normalize to 0-1 range (avoid division by zero)
            if score_range > 0:
                normalized_score = (float(score) - min_score) / score_range
            else:
                normalized_score = 1.0 if len(documents) == 1 else 0.5
            doc["rerank_score"] = normalized_score

        # Sort by rerank score and return top_k
        reranked = sorted(documents, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
