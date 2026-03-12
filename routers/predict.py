from fastapi import APIRouter, HTTPException, Query
from schemas.request import PredictRequest, BatchPredictRequest
from schemas.response import PredictResponse, BatchPredictResponse
from models.registry import get_model
from models.llm import call_claude
from utils.logger import log_request
from datetime import datetime
from typing import Optional
import uuid

router = APIRouter()


# ─── POST /predict/{model_name} ──────────────────────────────────────────────
# Path param: model_name | Query param: session_id | Body: PredictRequest
@router.post("/{model_name}", response_model=PredictResponse)
async def predict(
    model_name: str,
    body: PredictRequest,
    session_id: Optional[str] = Query(None, description="Pass existing session ID to group requests"),
    verbose: bool = Query(False, description="Include extra metadata in response"),
):
    """
    Run a single prediction using the specified model.
    
    - **model_name**: which AI persona to use (analyst, creative, coder, summarizer)
    - **session_id**: optional, groups this call into a named session
    - **verbose**: if true, logs extra metadata
    - **body**: input text, temperature, max_tokens, optional system_hint
    """
    model = get_model(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    if not model["active"]:
        raise HTTPException(status_code=403, detail=f"Model '{model_name}' is currently inactive.")

    # Use model defaults if not overridden in request
    temperature = body.temperature if body.temperature is not None else model["default_temperature"]
    max_tokens = body.max_tokens if body.max_tokens is not None else model["default_max_tokens"]

    try:
        output, tokens = await call_claude(
            user_text=body.text,
            system_prompt=model["persona"],
            temperature=temperature,
            max_tokens=max_tokens,
            system_hint=body.system_hint,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {str(e)}")

    sid = log_request(model_name, body.text, output, session_id)

    return PredictResponse(
        model=model_name,
        input_text=body.text,
        output=output,
        tokens_used=tokens if verbose else None,
        temperature=temperature,
        session_id=sid,
        timestamp=datetime.utcnow(),
    )


# ─── POST /predict/{model_name}/batch ────────────────────────────────────────
# Path param: model_name | Body: list of texts
@router.post("/{model_name}/batch", response_model=BatchPredictResponse)
async def batch_predict(
    model_name: str,
    body: BatchPredictRequest,
    session_id: Optional[str] = Query(None, description="Group batch under a session ID"),
):
    """
    Run multiple predictions in one request (max 10 texts).
    
    - **model_name**: which AI persona to use
    - **body.texts**: list of input strings (max 10)
    - **session_id**: optional session grouping
    """
    model = get_model(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    if not model["active"]:
        raise HTTPException(status_code=403, detail=f"Model '{model_name}' is inactive.")

    temperature = body.temperature or model["default_temperature"]
    max_tokens = body.max_tokens or model["default_max_tokens"]

    sid = session_id or str(uuid.uuid4())[:8]
    results = []

    for text in body.texts:
        try:
            output, tokens = await call_claude(
                user_text=text,
                system_prompt=model["persona"],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            output = f"[ERROR] {str(e)}"
            tokens = 0

        log_request(model_name, text, output, sid)
        results.append(PredictResponse(
            model=model_name,
            input_text=text,
            output=output,
            tokens_used=tokens,
            temperature=temperature,
            session_id=sid,
            timestamp=datetime.utcnow(),
        ))

    return BatchPredictResponse(
        model=model_name,
        results=results,
        total_processed=len(results),
    )


# ─── GET /predict/compare ────────────────────────────────────────────────────
# Query params: text, models (multiple)
@router.get("/compare", response_model=list[PredictResponse])
async def compare_models(
    text: str = Query(..., description="Text to run through all selected models"),
    models: list[str] = Query(default=["analyst", "creative"], description="Models to compare"),
    temperature: float = Query(0.7, ge=0.0, le=1.0),
):
    """
    Send the same text to multiple models and compare outputs side by side.
    
    - **text**: the input text
    - **models**: list of model names (e.g. ?models=analyst&models=coder)
    - **temperature**: shared temperature for all models
    """
    results = []
    sid = str(uuid.uuid4())[:8]

    for model_name in models:
        model = get_model(model_name)
        if not model or not model["active"]:
            continue
        try:
            output, tokens = await call_claude(
                user_text=text,
                system_prompt=model["persona"],
                temperature=temperature,
                max_tokens=model["default_max_tokens"],
            )
        except Exception as e:
            output = f"[ERROR] {str(e)}"
            tokens = 0

        log_request(model_name, text, output, sid)
        results.append(PredictResponse(
            model=model_name,
            input_text=text,
            output=output,
            tokens_used=tokens,
            temperature=temperature,
            session_id=sid,
            timestamp=datetime.utcnow(),
        ))

    return results
