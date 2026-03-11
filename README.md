# 🤖 Multi-Model AI Playground API

A production-style FastAPI project that exposes multiple AI personas (backed by Claude) via a clean REST API. Built to practice **HTTP methods**, **path & query parameters**, **Pydantic schemas**, **async calls**, and **project structure**.

---

## 📁 Project Structure

```
ai_playground/
├── main.py                  # FastAPI app, middleware, router registration
├── requirements.txt
├── .env.example             # Copy to .env and add your API key
├── models/
│   ├── registry.py          # Model definitions + config management
│   └── llm.py               # Async Claude API caller
├── routers/
│   ├── predict.py           # POST /predict — single, batch, compare
│   ├── models.py            # GET/PUT /models — list and configure models
│   └── history.py           # GET/DELETE /history — session tracking
├── schemas/
│   ├── request.py           # Pydantic input models
│   └── response.py          # Pydantic output models
└── utils/
    └── logger.py            # In-memory history store
```

---

## 🚀 Setup & Run

```bash
# 1. Clone / download the project
cd ai_playground

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 5. Run the server
uvicorn main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🔗 API Endpoints

### Models
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/models` | List all models (query: `active_only`, `sort_by`) |
| `GET` | `/models/{model_name}` | Get a specific model's info |
| `PUT` | `/models/{model_name}/config` | Update model config |

### Predict
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/{model_name}` | Single prediction (query: `session_id`, `verbose`) |
| `POST` | `/predict/{model_name}/batch` | Batch predictions (up to 10 texts) |
| `GET` | `/predict/compare` | Compare same text across multiple models |

### History
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/history` | All history (query: `model`, `limit`, `offset`) |
| `GET` | `/history/{session_id}` | History for one session |
| `DELETE` | `/history/{session_id}` | Delete a session |
| `DELETE` | `/history` | Clear all history |

---

## 🧠 Available Models (Personas)

| Model | Best For | Default Temp |
|-------|----------|--------------|
| `analyst` | Research, reasoning, structured analysis | 0.3 |
| `creative` | Ideas, stories, brainstorming | 0.95 |
| `coder` | Code generation, debugging, tech explanations | 0.2 |
| `summarizer` | Condensing long text into key points | 0.2 |

---

## 📌 FastAPI Concepts Used

| Concept | Where Used |
|--------|------------|
| **Path parameters** | `/predict/{model_name}`, `/history/{session_id}` |
| **Query parameters** | `?active_only=true`, `?limit=10&offset=0`, `?models=analyst&models=coder` |
| **Request body (POST)** | `PredictRequest`, `BatchPredictRequest` |
| **Pydantic validation** | All schemas with `Field(ge=, le=, min_length=)` |
| **HTTP GET** | List models, get history |
| **HTTP POST** | Predictions (single + batch) |
| **HTTP PUT** | Update model config |
| **HTTP DELETE** | Delete session / clear history |
| **Async/await** | `call_claude()` in `models/llm.py` |
| **APIRouter** | Separate routers per domain |
| **Tags** | Swagger UI grouping |
| **HTTPException** | 404, 403, 502 error handling |

---

## 💡 Example Requests

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict/analyst?verbose=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "What are the pros and cons of microservices?"}'

# Compare models
curl "http://localhost:8000/predict/compare?text=Explain+AI&models=analyst&models=creative"

# Batch prediction
curl -X POST "http://localhost:8000/predict/coder/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Write a Python hello world", "Explain recursion"]}'

# Paginated history
curl "http://localhost:8000/history?model=analyst&limit=5&offset=0"
```
