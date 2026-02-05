import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile
from typing import Optional
from datetime import datetime
from app.core.document_processor import DocumentProcessor
from app.core.chunker import DocumentChunker
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.models.schemas import UploadResponse
from app.config import settings


class UploadService:
    """Orchestrate document upload and indexing pipeline"""

    def __init__(
        self,
        processor: DocumentProcessor,
        chunker: DocumentChunker,
        embedder: Embedder,
        vector_store: VectorStore
    ):
        self.processor = processor
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    async def process_upload(self, file: UploadFile) -> UploadResponse:
        """
        Process uploaded file: save → extract → chunk → embed → index

        Args:
            file: Uploaded file (PDF or DOCX)

        Returns:
            UploadResponse with resource ID and status
        """
        # Generate unique resource ID
        resource_id = str(uuid.uuid4())

        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx']:
            raise ValueError(f"Unsupported file type: {file_ext}")

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size_mb = file.file.tell() / (1024 * 1024)
        file.file.seek(0)  # Reset to beginning

        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File too large: {file_size_mb:.1f}MB (max: {settings.MAX_FILE_SIZE_MB}MB)"
            )

        print(f"Processing upload: {file.filename} ({file_size_mb:.1f}MB)")

        # Save uploaded file
        file_path = await self._save_file(file, resource_id)

        try:
            # 1. Extract text (with OCR if needed)
            pages = self.processor.process_document(str(file_path))

            # 2. Chunk document
            chunks = self.chunker.chunk_document(pages, resource_id, file.filename)

            if not chunks:
                raise ValueError("No text content extracted from document")

            # 3. Generate embeddings
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedder.embed_texts(texts)

            # 4. Prepare metadata (MUST include text for search results)
            metadatas = []
            uploaded_at = datetime.utcnow().isoformat()
            for chunk in chunks:
                metadatas.append({
                    "chunk_id": str(uuid.uuid4()),
                    "resource_id": resource_id,
                    "file_name": file.filename,
                    "page_number": chunk.page,
                    "text": chunk.text,  # Store full text for display
                    "uploaded_at": uploaded_at,
                    "deleted": False
                })

            # 5. Add to vector store and persist
            self.vector_store.add_documents(embeddings, metadatas)
            self.vector_store.save()

            print(f"Successfully indexed {len(chunks)} chunks from {file.filename}")

            return UploadResponse(
                resource_id=resource_id,
                filename=file.filename,
                num_chunks=len(chunks),
                status="success"
            )

        except Exception as e:
            # Clean up uploaded file on error
            if file_path.exists():
                file_path.unlink()
            raise e

    async def _save_file(self, file: UploadFile, resource_id: str) -> Path:
        """
        Save uploaded file to disk.

        Args:
            file: Uploaded file
            resource_id: Unique resource ID

        Returns:
            Path to saved file
        """
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Create unique filename
        file_ext = Path(file.filename).suffix
        file_path = upload_dir / f"{resource_id}{file_ext}"

        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        print(f"Saved file to {file_path}")
        return file_path
