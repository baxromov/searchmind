from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from typing import List
from app.config import settings
from app.models.schemas import PageContent, Chunk


class DocumentChunker:
    """Split documents into chunks using token-based splitting"""

    def __init__(self):
        # Load tokenizer for the embedding model
        self.tokenizer = AutoTokenizer.from_pretrained(settings.EMBEDDING_MODEL)

        # Initialize text splitter with token-based chunking
        self.splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=self.tokenizer,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        print(f"Initialized chunker: {settings.CHUNK_SIZE} tokens, {settings.CHUNK_OVERLAP} overlap")

    def chunk_document(
        self,
        pages: List[PageContent],
        resource_id: str,
        file_name: str
    ) -> List[Chunk]:
        """
        Chunk a document into overlapping text chunks.

        Args:
            pages: List of PageContent objects
            resource_id: Unique ID for the document
            file_name: Name of the file

        Returns:
            List of Chunk objects with metadata
        """
        chunks = []
        chunks_per_page = {}

        for page in pages:
            if not page.text.strip():
                continue

            # Split page text into chunks
            text_chunks = self.splitter.split_text(page.text)

            # Track how many chunks per page for logging
            chunks_per_page[page.page_num] = len(text_chunks)

            # Create Chunk objects with metadata
            # IMPORTANT: Each chunk stores the page it came from
            # Multiple chunks can have the same page_number
            for chunk_text in text_chunks:
                if chunk_text.strip():  # Skip empty chunks
                    chunks.append(Chunk(
                        text=chunk_text,
                        page=page.page_num,
                        resource_id=resource_id,
                        file_name=file_name
                    ))

        print(f"Created {len(chunks)} chunks from {len(pages)} pages")
        print(f"Chunks per page: {chunks_per_page}")
        return chunks
