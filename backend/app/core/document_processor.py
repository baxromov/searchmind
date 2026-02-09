import pdfplumber
from docx import Document
from typing import List, Optional
from pathlib import Path
from app.models.schemas import PageContent
from app.config import settings


class DocumentProcessor:
    """Extract text from PDF/DOCX with optional OCR support"""

    def __init__(self):
        # Initialize PaddleOCR if enabled in settings
        self.ocr_engine: Optional[any] = None

        # Check if OCR is enabled in settings
        if not settings.USE_OCR:
            print("ℹ️  PaddleOCR disabled via settings (USE_OCR=False)")
            return

        # Lazy import - only import PaddleOCR if USE_OCR is enabled
        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                show_log=False
            )
            print("✅ PaddleOCR initialized - scanned document support enabled")
        except Exception as e:
            print(f"⚠️  Failed to initialize PaddleOCR: {e}")
            print("   Continuing without OCR support")

    def process_document(self, file_path: str) -> List[PageContent]:
        """
        Process a document and extract text from all pages.

        Args:
            file_path: Path to PDF or DOCX file

        Returns:
            List of PageContent objects
        """
        file_path = Path(file_path)

        if file_path.suffix.lower() == '.pdf':
            return self._process_pdf(str(file_path))
        elif file_path.suffix.lower() == '.docx':
            return self._process_docx(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _process_pdf(self, file_path: str) -> List[PageContent]:
        """Extract text from PDF with OCR fallback"""
        pages = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Try text extraction first
                text = page.extract_text() or ""

                # If text is sparse, use OCR
                if self._needs_ocr(text):
                    print(f"Page {page_num} needs OCR (sparse text)")
                    text = self._ocr_page(file_path, page_num)

                pages.append(PageContent(text=text, page_num=page_num))

        print(f"Processed PDF: {len(pages)} pages")
        return pages

    def _process_docx(self, file_path: str) -> List[PageContent]:
        """Extract text from DOCX"""
        doc = Document(file_path)

        # Combine all paragraphs into one page
        # (DOCX doesn't have clear page boundaries)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

        pages = [PageContent(text=text, page_num=1)]

        print(f"Processed DOCX: {len(text)} characters")
        return pages

    def _needs_ocr(self, text: str) -> bool:
        """
        Determine if a page needs OCR based on text content.

        Heuristic: If extracted text is very short, likely scanned.
        """
        # Only use OCR if available and text is sparse
        if not self.ocr_engine:
            return False
        return len(text.strip()) < 50

    def _ocr_page(self, pdf_path: str, page_num: int) -> str:
        """
        Run OCR on a specific PDF page.

        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-indexed)

        Returns:
            Extracted text
        """
        if not self.ocr_engine:
            print(f"⚠️  OCR requested but not available for page {page_num}")
            return ""

        try:
            # Import dependencies only when needed
            from pdf2image import convert_from_path
            import numpy as np

            # Convert PDF page to image
            images = convert_from_path(
                pdf_path,
                first_page=page_num,
                last_page=page_num,
                dpi=200  # Good balance between quality and speed
            )

            if not images:
                return ""

            # Run PaddleOCR
            result = self.ocr_engine.ocr(np.array(images[0]), cls=True)

            # Extract text from OCR result
            if result and result[0]:
                text = " ".join([line[1][0] for line in result[0]])
                return text
            else:
                return ""

        except Exception as e:
            print(f"OCR failed for page {page_num}: {e}")
            return ""
