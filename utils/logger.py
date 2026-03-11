from datetime import datetime
from typing import List, Optional
import uuid

# In-memory store: { session_id: [list of entries] }
_history: dict[str, list] = {}


def log_request(
    model: str,
    input_text: str,
    output: str,
    session_id: Optional[str] = None,
) -> str:
    """Log a prediction and return the session_id used."""
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    entry = {
        "session_id": session_id,
        "model": model,
        "input_text": input_text,
        "output": output,
        "timestamp": datetime.utcnow(),
    }

    if session_id not in _history:
        _history[session_id] = []
    _history[session_id].append(entry)
    return session_id


def get_all_history(
    model_filter: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[int, list]:
    """Return paginated history, optionally filtered by model."""
    all_entries = []
    for entries in _history.values():
        all_entries.extend(entries)

    # Sort newest first
    all_entries.sort(key=lambda x: x["timestamp"], reverse=True)

    if model_filter:
        all_entries = [e for e in all_entries if e["model"] == model_filter]

    total = len(all_entries)
    paginated = all_entries[offset: offset + limit]
    return total, paginated


def get_session_history(session_id: str) -> list:
    return _history.get(session_id, [])


def delete_session(session_id: str) -> bool:
    if session_id in _history:
        del _history[session_id]
        return True
    return False


def clear_all_history() -> int:
    count = sum(len(v) for v in _history.values())
    _history.clear()
    return count
