from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
from app.models.schemas import Resource, ChunkDetail
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


class PaginatedResourcesResponse(BaseModel):
    """Paginated response for resources"""
    resources: List[Resource]
    total: int
    offset: int
    limit: int
    has_more: bool


@router.get("", response_model=PaginatedResourcesResponse)
async def list_resources(
    offset: int = Query(default=0, ge=0, description="Number of resources to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Number of resources to return")
):
    """
    Get uploaded resources with pagination.

    Args:
        offset: Number of resources to skip
        limit: Maximum number of resources to return

    Returns:
        Paginated list of resources with metadata
    """
    from app.main import resource_service

    if not resource_service:
        raise HTTPException(status_code=503, detail="Resource service not initialized")

    try:
        all_resources = await resource_service.get_all_resources()
        total = len(all_resources)

        # Apply pagination
        paginated_resources = all_resources[offset:offset + limit]
        has_more = offset + limit < total

        return PaginatedResourcesResponse(
            resources=paginated_resources,
            total=total,
            offset=offset,
            limit=limit,
            has_more=has_more
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}/chunks", response_model=List[ChunkDetail])
async def get_resource_chunks(resource_id: str):
    """
    Get all chunks for a specific resource.

    Args:
        resource_id: The resource ID

    Returns:
        List of chunk details
    """
    from app.main import resource_service

    if not resource_service:
        raise HTTPException(status_code=503, detail="Resource service not initialized")

    try:
        chunks = await resource_service.get_resource_chunks(resource_id)
        return chunks
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}/file")
async def download_resource_file(resource_id: str):
    """
    Download the original uploaded file for a resource.

    Args:
        resource_id: The resource ID

    Returns:
        FileResponse with the original file
    """
    upload_dir = Path(settings.UPLOAD_DIR)

    # Try to find the file (could be .pdf or .docx)
    for ext in ['.pdf', '.docx']:
        file_path = upload_dir / f"{resource_id}{ext}"
        if file_path.exists():
            # Get original filename from metadata
            from app.main import resource_service
            try:
                resources = await resource_service.get_all_resources()
                original_filename = None
                for resource in resources:
                    if resource.resource_id == resource_id:
                        original_filename = resource.filename
                        break

                if not original_filename:
                    original_filename = f"{resource_id}{ext}"

                return FileResponse(
                    path=str(file_path),
                    filename=original_filename,
                    media_type='application/octet-stream'
                )
            except Exception:
                # Fallback to generic filename if metadata lookup fails
                return FileResponse(
                    path=str(file_path),
                    filename=f"{resource_id}{ext}",
                    media_type='application/octet-stream'
                )

    raise HTTPException(status_code=404, detail=f"File not found for resource: {resource_id}")


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str):
    """
    Delete a resource and all its chunks.

    Args:
        resource_id: The resource ID to delete

    Returns:
        Success message with deletion count
    """
    from app.main import resource_service

    if not resource_service:
        raise HTTPException(status_code=503, detail="Resource service not initialized")

    try:
        deleted_count = await resource_service.delete_resource(resource_id)
        return {
            "status": "success",
            "message": f"Resource deleted successfully",
            "resource_id": resource_id,
            "chunks_deleted": deleted_count
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
