import faiss
import pickle
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
from app.config import settings


class VectorStore:
    """FAISS vector store with metadata management"""

    def __init__(self, dimension: int, index_path: str):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Initialize FAISS index (Inner Product for cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)

        # Parallel array for metadata (same indices as FAISS)
        self.metadata_store: List[Dict] = []

        # Try to load existing index
        self._load_if_exists()

    def add_documents(self, embeddings: np.ndarray, metadatas: List[Dict]):
        """
        Add documents to the index.

        Args:
            embeddings: Normalized embeddings (for cosine similarity)
            metadatas: List of metadata dicts (one per embedding)
        """
        if embeddings.shape[0] != len(metadatas):
            raise ValueError("Number of embeddings must match number of metadata entries")

        # Ensure embeddings are normalized for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add to FAISS index
        self.index.add(embeddings)

        # Add to metadata store
        self.metadata_store.extend(metadatas)

        print(f"Added {len(metadatas)} documents. Total: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, k: int = 20) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding (will be normalized)
            k: Number of results to return

        Returns:
            List of (metadata, similarity_score) tuples
        """
        if self.index.ntotal == 0:
            return []

        # Normalize query for cosine similarity
        faiss.normalize_L2(query_embedding)

        # Search FAISS index
        k = min(k, self.index.ntotal)  # Don't request more than available
        scores, indices = self.index.search(query_embedding, k)

        # Combine with metadata (filter out deleted resources)
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.metadata_store):  # Safety check
                metadata = self.metadata_store[idx]
                # Skip deleted resources
                if not metadata.get('deleted', False):
                    results.append((metadata, float(score)))

        return results

    def save(self):
        """Persist index and metadata to disk"""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"

        # Save FAISS index
        faiss.write_index(self.index, str(index_file))

        # Save metadata
        with open(metadata_file, "wb") as f:
            pickle.dump(self.metadata_store, f)

        print(f"Saved index with {self.index.ntotal} vectors to {self.index_path}")

    def load(self):
        """Load index and metadata from disk"""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"

        if not index_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(f"Index files not found at {self.index_path}")

        # Load FAISS index
        self.index = faiss.read_index(str(index_file))

        # Load metadata
        with open(metadata_file, "rb") as f:
            self.metadata_store = pickle.load(f)

        print(f"Loaded index with {self.index.ntotal} vectors from {self.index_path}")

    def _load_if_exists(self):
        """Try to load existing index on initialization"""
        try:
            self.load()
        except FileNotFoundError:
            print(f"No existing index found at {self.index_path}. Starting fresh.")

    def get_total_documents(self) -> int:
        """Get total number of documents in the index"""
        return self.index.ntotal

    def get_all_resources(self) -> List[Dict]:
        """
        Get all resources with metadata.

        Returns:
            List of dicts with resource_id, filename, num_chunks, uploaded_at
        """
        # Group chunks by resource_id
        resource_map = {}
        for metadata in self.metadata_store:
            # Skip deleted resources
            if metadata.get('deleted', False):
                continue

            resource_id = metadata.get('resource_id')
            if not resource_id:
                continue

            if resource_id not in resource_map:
                resource_map[resource_id] = {
                    'resource_id': resource_id,
                    'filename': metadata.get('file_name', 'unknown'),
                    'num_chunks': 0,
                    'uploaded_at': metadata.get('uploaded_at', '')
                }

            resource_map[resource_id]['num_chunks'] += 1

        return list(resource_map.values())

    def get_chunks_by_resource(self, resource_id: str) -> List[Dict]:
        """
        Get all chunks for a specific resource.

        Args:
            resource_id: The resource ID to filter by

        Returns:
            List of dicts with chunk_id, text, page_number
        """
        chunks = []
        for metadata in self.metadata_store:
            # Skip deleted resources
            if metadata.get('deleted', False):
                continue

            if metadata.get('resource_id') == resource_id:
                chunks.append({
                    'chunk_id': metadata.get('chunk_id', ''),
                    'text': metadata.get('text', ''),
                    'page_number': metadata.get('page_number', 0)
                })

        return chunks

    def delete_resource(self, resource_id: str) -> int:
        """
        Soft-delete a resource by marking all its chunks as deleted.

        Args:
            resource_id: The resource ID to delete

        Returns:
            Number of chunks marked as deleted
        """
        deleted_count = 0
        for metadata in self.metadata_store:
            if metadata.get('resource_id') == resource_id and not metadata.get('deleted', False):
                metadata['deleted'] = True
                deleted_count += 1

        # Save the updated metadata
        if deleted_count > 0:
            self.save()

        return deleted_count
