from fastapi import APIRouter, HTTPException, Query
from schemas.response import HistoryResponse, HistoryItem
from utils.logger import get_all_history, get_session_history, delete_session, clear_all_history
from typing import Optional

router = APIRouter()


# ─── GET /history ─────────────────────────────────────────────────────────────
# Query params: model, limit, offset (pagination)
@router.get("/", response_model=HistoryResponse)
def list_history(
    model: Optional[str] = Query(None, description="Filter by model name"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Skip this many results"),
):
    """
    Get all prediction history with optional filtering and pagination.
    
    - **model**: filter by model name (analyst, creative, coder, summarizer)
    - **limit**: how many items to return (max 100)
    - **offset**: how many items to skip (for pagination)
    """
    total, items = get_all_history(model_filter=model, limit=limit, offset=offset)
    return HistoryResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[HistoryItem(**i) for i in items],
    )


# ─── GET /history/{session_id} ────────────────────────────────────────────────
# Path param: session_id
@router.get("/{session_id}", response_model=list[HistoryItem])
def get_session(session_id: str):
    """
    Get all requests made under a specific session ID.
    
    - **session_id**: the session ID returned from /predict
    """
    items = get_session_history(session_id)
    if not items:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return [HistoryItem(**i) for i in items]


# ─── DELETE /history/{session_id} ────────────────────────────────────────────
# Path param: session_id
@router.delete("/{session_id}")
def delete_session_history(session_id: str):
    """
    Delete all history for a specific session.
    
    - **session_id**: session to delete
    """
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return {"message": f"Session '{session_id}' deleted successfully."}


# ─── DELETE /history ──────────────────────────────────────────────────────────
@router.delete("/")
def clear_history():
    """
    Clear ALL prediction history (use with caution).
    """
    count = clear_all_history()
    return {"message": f"Cleared {count} history entries."}
