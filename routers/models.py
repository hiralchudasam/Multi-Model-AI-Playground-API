from fastapi import APIRouter, HTTPException, Query
from schemas.response import ModelInfo
from schemas.request import ModelConfigUpdate
from models.registry import get_all_models, get_model, update_model_config
from typing import Optional

router = APIRouter()


# ─── GET /models ──────────────────────────────────────────────────────────────
# Returns a list of all available AI models/personas.
# Query param : active_only → if True, only return models that are active
# Query param : sort_by     → sort results by 'name' or 'temperature'
@router.get("/", response_model=list[ModelInfo])
def list_models(
    active_only: bool = Query(False, description="Return only active models"),
    sort_by: Optional[str] = Query(None, description="Sort by: 'name' or 'temperature'"),
):
    """
    List all available AI models/personas.

    - **active_only**: filter out inactive models
    - **sort_by**: sort results by name or default_temperature
    """
    # Fetch all models from the registry
    models = get_all_models()

    # Filter to active only if requested
    if active_only:
        models = [m for m in models if m["active"]]

    # Sort by name alphabetically or by temperature (lowest to highest)
    if sort_by == "name":
        models.sort(key=lambda x: x["name"])
    elif sort_by == "temperature":
        models.sort(key=lambda x: x["default_temperature"])

    return models


# ─── GET /models/{model_name} ─────────────────────────────────────────────────
# Returns details for a single model by its name.
# Path param : model_name → the name of the model (e.g. analyst, coder)
@router.get("/{model_name}", response_model=ModelInfo)
def get_model_info(model_name: str):
    """
    Get details about a specific model by name.

    - **model_name**: one of analyst, creative, coder, summarizer
    """
    # Look up model — returns None if not found
    model = get_model(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    return model


# ─── PUT /models/{model_name}/config ─────────────────────────────────────────
# Updates the default configuration for a specific model.
# Path param : model_name → the model to update
# Body       : ModelConfigUpdate → fields to update (all optional)
# Note       : Changes are stored in memory and reset on server restart
@router.put("/{model_name}/config", response_model=ModelInfo)
def update_config(model_name: str, config: ModelConfigUpdate):
    """
    Update default config for a model (temperature, max_tokens, active status).

    - **model_name**: model to update
    - **body**: fields to update (all optional — only send what you want to change)
    """
    # Apply the config overrides and return the updated model
    updated = update_model_config(model_name, config.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    return updated
