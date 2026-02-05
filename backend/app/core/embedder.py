from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from app.config import settings


class Embedder:
    """Generate embeddings using multilingual sentence transformer"""

    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        Returns normalized embeddings for cosine similarity.
        """
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=len(texts) > 50
        )
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query"""
        return self.embed_texts([query])
