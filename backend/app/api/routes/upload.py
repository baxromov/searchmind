from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and index a document (PDF or DOCX).

    The document will be:
    1. Saved to disk
    2. Processed (with OCR if needed)
    3. Chunked into overlapping segments
    4. Embedded and indexed for search

    Returns:
        UploadResponse with resource_id and status
    """
    # Service will be injected via dependency
    from app.main import upload_service

    try:
        result = await upload_service.process_upload(file)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload processing failed")
