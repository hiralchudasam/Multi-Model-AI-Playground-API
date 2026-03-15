from fastapi import APIRouter, HTTPException, Query
from schemas.request import PredictRequest, BatchPredictRequest
from schemas.response import PredictResponse, BatchPredictResponse
from models.registry import get_model
from models.llm import call_gemini
from utils.logger import log_request
from datetime import datetime
from typing import Optional
import uuid

router = APIRouter()


# ─── POST /predict/{model_name} ──────────────────────────────────────────────
# Runs a single prediction for the given model persona.
# Path param  : model_name   → which AI persona to use
# Query param : session_id   → optional, groups multiple calls under one session
# Query param : verbose      → if True, includes token usage in response
# Body        : PredictRequest → input text, temperature, max_tokens, system_hint
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
    - **verbose**: if true, includes token count in response
    - **body**: input text, temperature, max_tokens, optional system_hint
    """
    # Check if the model exists in the registry
    model = get_model(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")

    # Reject requests to inactive models
    if not model["active"]:
        raise HTTPException(status_code=403, detail=f"Model '{model_name}' is currently inactive.")

    # Use request values if provided, otherwise fall back to model defaults
    temperature = body.temperature if body.temperature is not None else model["default_temperature"]
    max_tokens = body.max_tokens if body.max_tokens is not None else model["default_max_tokens"]

    # Call the LLM with the model's persona as the system prompt
    try:
        output, tokens = await call_gemini(
            user_text=body.text,
            system_prompt=model["persona"],
            temperature=temperature,
            max_tokens=max_tokens,
            system_hint=body.system_hint,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {str(e)}")

    # Log this request to in-memory history and get back the session ID
    sid = log_request(model_name, body.text, output, session_id)

    return PredictResponse(
        model=model_name,
        input_text=body.text,
        output=output,
        tokens_used=tokens if verbose else None,  # only show tokens if verbose=True
        temperature=temperature,
        session_id=sid,
        timestamp=datetime.utcnow(),
    )


# ─── POST /predict/{model_name}/batch ────────────────────────────────────────
# Runs predictions for multiple texts in a single request (max 10).
# Path param  : model_name       → which AI persona to use
# Query param : session_id       → groups all batch results under one session
# Body        : BatchPredictRequest → list of texts, temperature, max_tokens
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
    # Validate the model exists and is active
    model = get_model(model_name)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found.")
    if not model["active"]:
        raise HTTPException(status_code=403, detail=f"Model '{model_name}' is inactive.")

    # Fall back to model defaults if not provided in request
    temperature = body.temperature or model["default_temperature"]
    max_tokens = body.max_tokens or model["default_max_tokens"]

    # Generate a shared session ID for all items in this batch
    sid = session_id or str(uuid.uuid4())[:8]
    results = []

    # Loop through each text and call LLM individually
    for text in body.texts:
        try:
            output, tokens = await call_gemini(
                user_text=text,
                system_prompt=model["persona"],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            # Don't fail the whole batch — log error and continue
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
# Sends the same text to multiple models and returns all responses side by side.
# Query param : text       → the input text to send to all models
# Query param : models     → list of model names to compare (multi-value)
# Query param : temperature → shared temperature for all models
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

    # All comparisons share the same session ID for easy history lookup
    sid = str(uuid.uuid4())[:8]

    for model_name in models:
        model = get_model(model_name)

        # Silently skip invalid or inactive models instead of failing
        if not model or not model["active"]:
            continue

        try:
            output, tokens = await call_gemini(
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
