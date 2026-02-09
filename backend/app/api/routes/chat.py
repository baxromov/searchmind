from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest

router = APIRouter()


@router.post("/chat/stream")
async def chat_stream(request: Request, chat_request: ChatRequest):
    """
    Stream chat responses using RAG approach.

    This endpoint uses Server-Sent Events (SSE) to stream the response in real-time.

    Event types:
    - sources: List of retrieved document sources
    - query: Rewritten query used for search
    - chunk: Piece of generated answer text
    - done: Completion signal with timing info
    - error: Error information if something fails

    Args:
        chat_request: Contains user message and chat history

    Returns:
        StreamingResponse with text/event-stream content type
    """
    try:
        chat_service = request.app.state.chat_service

        async def event_generator():
            async for event in chat_service.chat_stream(
                query=chat_request.message,
                history=[msg.model_dump() for msg in chat_request.history] if chat_request.history else None
            ):
                yield event

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
