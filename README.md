# 🤖 Multi-Model AI Playground API

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4?style=flat&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

A production-style REST API built with **FastAPI** that exposes multiple AI personas powered by **Google Gemini**. Send text to different AI "models" — each one thinks and responds differently based on its persona.

---

## 🎯 What Does It Do?

Instead of one generic AI endpoint, you get **4 specialized AI personas**:

| Persona | Best For | Temperature |
|---------|----------|-------------|
| 🧠 `analyst` | Research, reasoning, structured analysis | 0.3 (focused) |
| 🎨 `creative` | Ideas, stories, brainstorming | 0.95 (wild) |
| 💻 `coder` | Code generation, debugging, tech help | 0.2 (precise) |
| 📝 `summarizer` | Condensing long text into key points | 0.2 (concise) |

Same question → 4 very different answers. That's the playground.

---

## 📁 Project Structure

```
ai_playground/
├── main.py                  # FastAPI app, middleware, router registration
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
├── models/
│   ├── registry.py          # AI persona definitions and config management
│   └── llm.py               # Async LLM API caller
├── routers/
│   ├── predict.py           # POST /predict — single, batch, compare
│   ├── models.py            # GET/PUT /models — list and configure models
│   └── history.py           # GET/DELETE /history — session tracking
├── schemas/
│   ├── request.py           # Pydantic input validation models
│   └── response.py          # Pydantic output models
└── utils/
    └── logger.py            # In-memory session history store
```

---

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/hiralchudasam/Multi-Model-AI-Playground-API.git
cd Multi-Model-AI-Playground-API
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Open `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```
> Get your free API key at 👉 [aistudio.google.com](https://aistudio.google.com)

### 5. Run the server
```bash
uvicorn main:app --reload
```

Open 👉 **http://localhost:8000/docs** for interactive Swagger UI

---

## 🔗 API Endpoints

### 📦 Models
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/models` | List all models (filter & sort via query params) |
| `GET` | `/models/{model_name}` | Get specific model details |
| `PUT` | `/models/{model_name}/config` | Update model configuration |

### 🤖 Predict
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/{model_name}` | Single prediction |
| `POST` | `/predict/{model_name}/batch` | Batch predictions (up to 10 texts) |
| `GET` | `/predict/compare` | Compare same text across multiple models |

### 📜 History
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/history` | All history with pagination and filtering |
| `GET` | `/history/{session_id}` | History for a specific session |
| `DELETE` | `/history/{session_id}` | Delete a session |
| `DELETE` | `/history` | Clear all history |

---

## 💡 Example Requests

### Single Prediction
```bash
curl -X POST "http://localhost:8000/predict/analyst?verbose=true" \
  -H "Content-Type: application/json" \
  -d '{"text": "What are pros and cons of microservices?"}'
```

### Batch Prediction
```bash
curl -X POST "http://localhost:8000/predict/coder/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Write a Python hello world", "Explain recursion"]}'
```

### Compare Models
```bash
curl "http://localhost:8000/predict/compare?text=Explain+AI&models=analyst&models=creative"
```

### Paginated History
```bash
curl "http://localhost:8000/history?model=analyst&limit=5&offset=0"
```

---

## 🧠 FastAPI Concepts Covered

| Concept | Where Used |
|---------|------------|
| Path parameters | `/predict/{model_name}`, `/history/{session_id}` |
| Query parameters | `?limit=10&offset=0`, `?models=analyst&models=coder` |
| Request body | `PredictRequest`, `BatchPredictRequest` with Pydantic |
| HTTP GET | List models, get history |
| HTTP POST | Single and batch predictions |
| HTTP PUT | Update model config |
| HTTP DELETE | Delete session / clear history |
| Async/await | LLM API call in `models/llm.py` |
| APIRouter | Separate router files per domain |
| HTTPException | 404, 403, 502 error handling |

---

## 🛠️ Tech Stack

- **FastAPI** — Web framework
- **Google Gemini 1.5 Flash** — LLM backend (free tier)
- **Pydantic** — Request/response validation
- **httpx** — Async HTTP client
- **uvicorn** — ASGI server

---

## 📄 License

MIT License — feel free to use this project for learning and portfolio purposes.
