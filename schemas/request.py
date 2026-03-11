from pydantic import BaseModel, Field
from typing import Optional, List


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Input text to process")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Creativity level (0=focused, 1=creative)")
    max_tokens: Optional[int] = Field(500, ge=50, le=2000, description="Max response length")
    system_hint: Optional[str] = Field(None, description="Extra instruction to customize behavior")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Explain how neural networks work",
                    "temperature": 0.5,
                    "max_tokens": 300,
                    "system_hint": "Use simple language"
                }
            ]
        }
    }


class BatchPredictRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=10, description="List of texts (max 10)")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(300, ge=50, le=1000)


class ModelConfigUpdate(BaseModel):
    default_temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    default_max_tokens: Optional[int] = Field(None, ge=50, le=2000)
    active: Optional[bool] = None
