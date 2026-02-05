from pathlib import Path
from typing import List
from app.core.vector_store import VectorStore
from app.models.schemas import Resource, ChunkDetail
from app.config import settings


class ResourceService:
    """Service for managing resources (uploaded documents)"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.upload_dir = Path(settings.UPLOAD_DIR)

    async def get_all_resources(self) -> List[Resource]:
        """
        Get all uploaded resources.

        Returns:
            List of Resource objects
        """
        resources_data = self.vector_store.get_all_resources()
        resources = [
            Resource(
                resource_id=r['resource_id'],
                filename=r['filename'],
                num_chunks=r['num_chunks'],
                uploaded_at=r['uploaded_at']
            )
            for r in resources_data
        ]
        return resources

    async def get_resource_chunks(self, resource_id: str) -> List[ChunkDetail]:
        """
        Get all chunks for a specific resource.

        Args:
            resource_id: The resource ID

        Returns:
            List of ChunkDetail objects

        Raises:
            ValueError: If resource not found
        """
        chunks_data = self.vector_store.get_chunks_by_resource(resource_id)

        if not chunks_data:
            raise ValueError(f"Resource not found: {resource_id}")

        chunks = [
            ChunkDetail(
                chunk_id=c['chunk_id'],
                text=c['text'],
                page_number=c['page_number']
            )
            for c in chunks_data
        ]
        return chunks

    async def delete_resource(self, resource_id: str) -> int:
        """
        Delete a resource and its associated file.

        Args:
            resource_id: The resource ID to delete

        Returns:
            Number of chunks deleted

        Raises:
            ValueError: If resource not found
        """
        # Mark chunks as deleted in vector store
        deleted_count = self.vector_store.delete_resource(resource_id)

        if deleted_count == 0:
            raise ValueError(f"Resource not found: {resource_id}")

        # Delete physical file (try both .pdf and .docx)
        for ext in ['.pdf', '.docx']:
            file_path = self.upload_dir / f"{resource_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                print(f"Deleted file: {file_path}")
                break

        return deleted_count
