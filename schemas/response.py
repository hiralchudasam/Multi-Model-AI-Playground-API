from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class PredictResponse(BaseModel):
    model: str
    input_text: str
    output: str
    tokens_used: Optional[int]
    temperature: float
    session_id: str
    timestamp: datetime


class BatchPredictResponse(BaseModel):
    model: str
    results: List[PredictResponse]
    total_processed: int


class ModelInfo(BaseModel):
    name: str
    description: str
    persona: str
    default_temperature: float
    default_max_tokens: int
    active: bool


class HistoryItem(BaseModel):
    session_id: str
    model: str
    input_text: str
    output: str
    timestamp: datetime


class HistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[HistoryItem]
