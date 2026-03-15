from fastapi import APIRouter, HTTPException, Query
from schemas.request import PredictRequest, BatchPredictRequest
from schemas.response import PredictResponse, BatchPredictResponse
from models.registry import get_model
from models.llm import call_gemini
from utils.logger
