from fastapi import APIRouter, HTTPException, Query
from schemas.response import HistoryResponse, HistoryItem
from utils.logger import get_all_history, get_session_history, delete_session, clear_all_history
from typing import Optional

router = APIRouter()


# ─── GET /history ─────────────────────────────────────────────────────────────
# Returns paginated prediction history across all sessions.
# Query param : model  → filter results to a specific model name
# Query param : limit  → how many results to return per page (default 10, max 100)
# Query param : offset → how many results to skip (used for pagination)
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
    # Fetch total count and paginated items from the in-memory store
    total, items = get_all_history(model_filter=model, limit=limit, offset=offset)

    return HistoryResponse(
        total=total,       # total matching records (before pagination)
        limit=limit,       # page size used
        offset=offset,     # how many were skipped
        items=[HistoryItem(**i) for i in items],
    )


# ─── GET /history/{session_id} ────────────────────────────────────────────────
# Returns all prediction records for a specific session.
# Path param : session_id → the session ID returned from /predict endpoints
@router.get("/{session_id}", response_model=list[HistoryItem])
def get_session(session_id: str):
    """
    Get all requests made under a specific session ID.

    - **session_id**: the session ID returned from /predict
    """
    items = get_session_history(session_id)

    # Return 404 if no records found for this session
    if not items:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    return [HistoryItem(**i) for i in items]


# ─── DELETE /history/{session_id} ────────────────────────────────────────────
# Deletes all prediction records for a specific session.
# Path param : session_id → the session to delete
@router.delete("/{session_id}")
def delete_session_history(session_id: str):
    """
    Delete all history for a specific session.

    - **session_id**: session to delete
    """
    deleted = delete_session(session_id)

    # Return 404 if the session doesn't exist
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    return {"message": f"Session '{session_id}' deleted successfully."}


# ─── DELETE /history ──────────────────────────────────────────────────────────
# Wipes all prediction history across all sessions.
# Use with caution — this cannot be undone (data is in-memory only).
@router.delete("/")
def clear_history():
    """
    Clear ALL prediction history (use with caution — cannot be undone).
    """
    count = clear_all_history()
    return {"message": f"Cleared {count} history entries."}
