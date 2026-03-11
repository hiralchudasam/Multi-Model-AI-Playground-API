from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import predict, models, history

app = FastAPI(
    title="🤖 Multi-Model AI Playground",
    description="""
    A LLM-powered API playground built with FastAPI + Claude.
    
    ## Features
    - 🧠 Multiple AI personas/models (Analyst, Creative, Coder, Summarizer)
    - 💬 Single & batch predictions
    - 📜 Session history tracking
    - ⚙️ Per-model configuration
    - 🔍 Rich query parameter support
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(predict.router, prefix="/predict", tags=["Predict"])
app.include_router(history.router, prefix="/history", tags=["History"])


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Multi-Model AI Playground!",
        "docs": "/docs",
        "available_models": ["analyst", "creative", "coder", "summarizer"],
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
