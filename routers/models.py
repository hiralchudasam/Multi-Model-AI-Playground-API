from fastapi import APIRouter, HTTPException, Query
from schemas.response import ModelInfo
from schemas.request import ModelConfigUpdate
from models.registry import get_all_models, get_model, update_model_config
from typing import Optional

router = APIRouter()


# ─── GET /models ────────────────────────────────────────────────────────────
# Query params: active_only (filter), sort_by (name or temperature)
@router.get("/", response_model=list[ModelInfo])
def list_models(
    active_only: bool = Query(False, description="Return only active models"),
    sort_by: Optional[str] = Query(None, description="Sort by: 'name' or 'temperature'"),
):
    """
    List all available AI models/personas.
    
    - **active_only**: filter inactive models out
    - **sort_by**: sort results by name or default_temperature
    """
    models = get_all_models()

    if active_only:
        models = [m for m in models if m["active"]]

    if sort_by == "name":
        models.sort(key=lambda x: x["name"])
    elif sort_by == "temperature":
        models.sort(key=lambda x: x["default_temperature"])

    return models


# ─── GET /models/{model_name} ────────────────────────────────────────────────
# Path param: model_name
@router.get("/{model_name}", response_model=ModelInfo)
def get_model_info(model_name: str):
    """
    Get details about a specific model by name.
    
    - **model_name**: one of analyst, creative, coder, summarizer
    """
    model = get_model(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    return model


# ─── PUT /models/{model_name}/config ─────────────────────────────────────────
# Path param + request body
@router.put("/{model_name}/config", response_model=ModelInfo)
def update_config(model_name: str, config: ModelConfigUpdate):
    """
    Update default config for a model (temperature, max_tokens, active status).
    
    - **model_name**: model to update
    - **body**: fields to update (all optional)
    """
    updated = update_model_config(model_name, config.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    return updated
