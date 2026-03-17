# 📚 FastAPI + LLM Integration — Complete Learning Guide

> This guide documents the complete journey of building a **Multi-Model AI Playground API** using FastAPI and Google Gemini. Written for developers who already know Python and want to switch to FastAPI for building production-style APIs.

---

## 📌 Table of Contents

1. [Why FastAPI?](#1-why-fastapi)
2. [Project Thinking Process](#2-project-thinking-process)
3. [Project Structure — Why It's Organized This Way](#3-project-structure)
4. [FastAPI Core Concepts](#4-fastapi-core-concepts)
   - Path Parameters
   - Query Parameters
   - Request Body
   - HTTP Methods
   - Pydantic Validation
   - APIRouter
   - HTTPException
   - Async/Await
5. [LLM Integration](#5-llm-integration)
6. [Google Gemini API](#6-google-gemini-api)
7. [Common Errors and Fixes](#7-common-errors-and-fixes)
8. [Git for Beginners](#8-git-for-beginners)
9. [API Testing with Swagger UI](#9-api-testing-with-swagger-ui)
10. [What to Learn Next](#10-what-to-learn-next)

---

## 1. Why FastAPI?

If you're coming from Flask or Django, here's why FastAPI is worth learning:

| Feature | Flask | Django | FastAPI |
|---------|-------|--------|---------|
| Speed | Medium | Slow | 🚀 Very Fast |
| Auto Docs | ❌ No | ❌ No | ✅ Yes (Swagger) |
| Type hints | Optional | Optional | Built-in |
| Async support | Limited | Limited | ✅ Native |
| Learning curve | Easy | Steep | Easy |
| Best for | Small APIs | Full web apps | Modern APIs |

FastAPI automatically generates interactive documentation at `/docs` — no extra work needed.

---

## 2. Project Thinking Process

### How to think before writing code

Before writing a single line, ask yourself:

**1. What does this API do?**
> "Users send text → choose an AI persona → get a response"

**2. What are the resources?**
> Models, Predictions, History — each becomes a router

**3. What HTTP methods do I need?**
> - GET → read data
> - POST → create/process data
> - PUT → update data
> - DELETE → remove data

**4. What are the inputs and outputs?**
> Inputs → Pydantic request schemas
> Outputs → Pydantic response schemas

**5. What can go wrong?**
> Model not found (404), model inactive (403), LLM fails (502)

### The golden rule
> Design your URLs around **resources**, not actions.
> ✅ `POST /predict/analyst` (resource = prediction, persona = analyst)
> ❌ `POST /run-analyst-prediction` (action-based, hard to scale)

---

## 3. Project Structure

```
ai_playground/
├── main.py              # Entry point — registers routers, middleware
├── models/
│   ├── registry.py      # Data layer — model definitions and config
│   └── llm.py           # Service layer — external API call
├── routers/
│   ├── predict.py       # Route handlers for predictions
│   ├── models.py        # Route handlers for model management
│   └── history.py       # Route handlers for session history
├── schemas/
│   ├── request.py       # What the API accepts (input)
│   └── response.py      # What the API returns (output)
└── utils/
    └── logger.py        # Helper — in-memory history store
```

### Why separate files?

- **routers/** → Each file owns one domain (predict, models, history). Easy to find, easy to modify.
- **schemas/** → Separating input/output validation from business logic keeps code clean.
- **models/** → Business logic (registry, LLM calls) is isolated from HTTP handling.
- **utils/** → Shared helpers that multiple routers can use.

> Rule of thumb: If a router file grows beyond 150 lines, split it further.

---

## 4. FastAPI Core Concepts

### 4.1 Path Parameters

Path parameters are **part of the URL** — they identify a specific resource.

```python
from fastapi import APIRouter
router = APIRouter()

# {model_name} is a path parameter
@router.get("/{model_name}")
def get_model(model_name: str):
    return {"model": model_name}
```

**URL:** `GET /models/analyst` → `model_name = "analyst"`

**When to use path params:**
- Identifying a specific resource: `/users/42`, `/models/analyst`
- Required values that are part of the resource identity

---

### 4.2 Query Parameters

Query parameters come **after the `?`** in the URL — they filter, sort, or paginate.

```python
from fastapi import Query
from typing import Optional

@router.get("/")
def list_models(
    active_only: bool = Query(False),           # optional, default False
    sort_by: Optional[str] = Query(None),       # optional, default None
    limit: int = Query(10, ge=1, le=100),       # optional, with validation
):
    pass
```

**URL:** `GET /models?active_only=true&sort_by=name&limit=5`

**When to use query params:**
- Filtering: `?model=analyst`
- Pagination: `?limit=10&offset=20`
- Sorting: `?sort_by=name`
- Optional flags: `?verbose=true`

**Multi-value query params (lists):**
```python
@router.get("/compare")
def compare(models: list[str] = Query(default=["analyst", "creative"])):
    pass
```
**URL:** `GET /compare?models=analyst&models=coder&models=creative`

---

### 4.3 Request Body

Request body is used with `POST` and `PUT` — it carries the main data payload.

```python
from pydantic import BaseModel, Field
from typing import Optional

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(500, ge=50, le=2000)
    system_hint: Optional[str] = None

@router.post("/{model_name}")
async def predict(model_name: str, body: PredictRequest):
    print(body.text)        # access fields directly
    print(body.temperature)
```

**Request:**
```json
POST /predict/analyst
{
  "text": "Explain neural networks",
  "temperature": 0.5
}
```

**Field validation shortcuts:**
- `...` → field is required (no default)
- `ge=0.0` → greater than or equal to 0.0
- `le=1.0` → less than or equal to 1.0
- `min_length=1` → minimum string length
- `max_length=5000` → maximum string length

---

### 4.4 HTTP Methods

```python
@router.get("/")          # Read data — safe, no side effects
@router.post("/")         # Create or process — has side effects
@router.put("/{id}")      # Update existing — replaces the resource
@router.patch("/{id}")    # Partial update — only changed fields
@router.delete("/{id}")   # Remove a resource
```

**In this project:**

```python
GET    /models                    # list all models
GET    /models/{model_name}       # get one model
PUT    /models/{model_name}/config # update model config
POST   /predict/{model_name}      # run prediction (has side effect = LLM call)
POST   /predict/{model_name}/batch # run batch predictions
GET    /predict/compare           # compare models (read-only, no side effects)
GET    /history                   # read history
DELETE /history/{session_id}      # delete a session
```

---

### 4.5 Pydantic Validation

Pydantic automatically validates incoming data and returns clear error messages.

```python
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    temperature: float = Field(0.7, ge=0.0, le=1.0)
```

If you send `temperature: 5.0`, FastAPI automatically returns:
```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

No manual validation code needed — Pydantic handles it all.

---

### 4.6 APIRouter

`APIRouter` lets you split routes across multiple files cleanly.

**In `routers/predict.py`:**
```python
from fastapi import APIRouter
router = APIRouter()

@router.post("/{model_name}")
async def predict(model_name: str):
    pass
```

**In `main.py`:**
```python
from routers import predict, models, history

app.include_router(predict.router, prefix="/predict", tags=["Predict"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(history.router, prefix="/history", tags=["History"])
```

The `prefix` is prepended to all routes in that router:
> `@router.post("/{model_name}")` + `prefix="/predict"` = `POST /predict/{model_name}`

The `tags` group routes in Swagger UI.

---

### 4.7 HTTPException

Use `HTTPException` to return proper error responses:

```python
from fastapi import HTTPException

@router.get("/{model_name}")
def get_model(model_name: str):
    model = find_model(model_name)

    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found."
        )

    if not model["active"]:
        raise HTTPException(
            status_code=403,
            detail=f"Model '{model_name}' is currently inactive."
        )

    return model
```

**Common status codes:**
| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | Default success |
| 201 | Created | After POST that creates resource |
| 400 | Bad Request | Invalid input from client |
| 403 | Forbidden | Resource exists but access denied |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable | Pydantic validation failed (automatic) |
| 502 | Bad Gateway | External API (LLM) failed |

---

### 4.8 Async/Await

FastAPI supports `async` natively — critical for I/O-bound operations like API calls.

```python
import httpx

# ❌ Blocking — freezes the server while waiting for response
def call_llm(text: str):
    response = requests.post(url, json=payload)  # blocks
    return response.json()

# ✅ Non-blocking — server handles other requests while waiting
async def call_llm(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)  # non-blocking
    return response.json()
```

**Rule:**
- Use `async def` for route handlers that call external APIs or databases
- Use `def` for simple, CPU-only logic
- Use `httpx.AsyncClient` instead of `requests` for async HTTP calls

---

## 5. LLM Integration

### How it works in this project

```
Request comes in
      ↓
Router validates path/query params + request body (Pydantic)
      ↓
Registry looks up the model's persona (system prompt)
      ↓
llm.py sends user text + persona to Gemini API (async)
      ↓
Response is logged to in-memory history
      ↓
Clean JSON response returned
```

### The persona pattern

Each "model" is really the same LLM with a different **system prompt**:

```python
# analyst persona — structured, data-driven
"You are a sharp analytical assistant. You break down problems
logically, use data-driven reasoning..."

# creative persona — imaginative, energetic
"You are a wildly creative assistant overflowing with ideas.
You think outside the box..."
```

Same question → different system prompt → completely different answer style.
This is called **prompt engineering** and is the foundation of most LLM products.

---

## 6. Google Gemini API

### Why Gemini for this project?
- ✅ Free tier: 15 requests/min, 1500 requests/day
- ✅ No credit card required to start
- ✅ Fast response times
- ✅ Good quality for most tasks

### Get your free API key
1. Go to 👉 [aistudio.google.com](https://aistudio.google.com)
2. Click **"Get API Key"** → **"Create API key"**
3. Add to your `.env`: `GEMINI_API_KEY=your_key_here`

### How the API call works

```python
import os
import httpx

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def call_gemini(user_text, system_prompt, temperature=0.7, max_tokens=500):
    api_key = os.getenv("GEMINI_API_KEY")

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]   # persona goes here
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_text}]}
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{GEMINI_URL}?key={api_key}",
            json=payload
        )
        response.raise_for_status()   # raises exception if status >= 400
        data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    tokens = data.get("usageMetadata", {}).get("candidatesTokenCount", 0)
    return text, tokens
```

### Temperature explained

| Temperature | Behavior | Best for |
|-------------|----------|----------|
| 0.0 – 0.3 | Focused, deterministic | Code, analysis, factual answers |
| 0.4 – 0.7 | Balanced | General purpose |
| 0.8 – 1.0 | Creative, varied | Brainstorming, stories, ideas |

---

## 7. Common Errors and Fixes

### ❌ `fatal: not a git repository`
**Cause:** Running git commands outside the project folder.
```bash
# Fix: navigate to your project folder first
cd ai_playground
git init
```

---

### ❌ `Author identity unknown`
**Cause:** Git doesn't know who you are.
```bash
git config --global user.email "your@email.com"
git config --global user.name "yourname"
```

---

### ❌ `remote: Repository not found`
**Cause:** The GitHub repo doesn't exist yet, or the URL is wrong.
```bash
# Fix: create repo on github.com first, then:
git remote remove origin
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

---

### ❌ `[rejected] main -> main (fetch first)`
**Cause:** GitHub has changes your local machine doesn't have (e.g. README created on GitHub).
```bash
# Fix: force push (safe for fresh repos only)
git push origin main --force
```

---

### ❌ `LF will be replaced by CRLF` warning
**Cause:** Windows uses different line endings than Linux/Mac.
```bash
# Fix: configure git to handle this automatically (run once)
git config --global core.autocrlf true
```
> This is just a warning, not an error. Your code works fine.

---

### ❌ `GEMINI_API_KEY environment variable not set`
**Cause:** `.env` file missing or not loaded.
```bash
# Fix 1: make sure .env file exists
cp .env.example .env

# Fix 2: add python-dotenv to main.py
from dotenv import load_dotenv
load_dotenv()  # add this at the top of main.py
```

---

### ❌ `422 Unprocessable Entity`
**Cause:** Request body doesn't match the Pydantic schema.
```bash
# Check: are you sending the correct Content-Type header?
curl -X POST "http://localhost:8000/predict/analyst" \
  -H "Content-Type: application/json" \    # ← this is required
  -d '{"text": "hello"}'
```

---

### ❌ `ModuleNotFoundError: No module named 'fastapi'`
**Cause:** Virtual environment not activated or packages not installed.
```bash
# Fix:
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## 8. Git for Beginners

### Commit message conventions

```
<type>: <short description>

Types:
feat     → new feature added
fix      → bug fix
refactor → code changed, no new feature
docs     → documentation only
chore    → config, dependencies, cleanup
test     → adding tests
```

**Examples:**
```bash
git commit -m "feat: add session history tracking"
git commit -m "fix: handle inactive model error correctly"
git commit -m "refactor: update LLM backend integration"
git commit -m "docs: update README with setup guide"
git commit -m "chore: pin dependency versions"
```

### Day-by-day push strategy

Don't push everything at once. Push in logical chunks:

| Day | What to push | Why |
|-----|-------------|-----|
| Day 1 | Project structure, schemas, config | Foundation — no secrets |
| Day 2 | LLM service, predict router | Core feature |
| Day 3 | History router | Secondary feature |
| Day 4 | Docs, comments, cleanup | Polish |

### Essential git commands

```bash
git init                          # initialize a new repo
git status                        # see what's changed
git add <file>                    # stage a file
git add .                         # stage all changed files
git commit -m "message"           # commit staged files
git push                          # push to GitHub
git pull                          # get latest from GitHub
git log --oneline                 # see commit history
git diff                          # see what changed
git remote -v                     # check remote URL
```

### Files to NEVER push

```gitignore
.env                  # API keys and secrets
__pycache__/          # Python bytecode
*.pyc                 # compiled Python files
venv/                 # virtual environment (too large, not needed)
.DS_Store             # Mac system file
```

Always create `.gitignore` **before** your first commit.

---

## 9. API Testing with Swagger UI

FastAPI auto-generates Swagger UI at `http://localhost:8000/docs`.

### How to test an endpoint in Swagger

1. Run server: `uvicorn main:app --reload`
2. Open `http://localhost:8000/docs`
3. Click on any endpoint
4. Click **"Try it out"**
5. Fill in parameters and body
6. Click **"Execute"**
7. See the response below

### Testing with curl

```bash
# GET request
curl "http://localhost:8000/models"

# GET with query params
curl "http://localhost:8000/models?active_only=true&sort_by=name"

# POST with body
curl -X POST "http://localhost:8000/predict/analyst" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is machine learning?"}'

# POST with path + query + body
curl -X POST "http://localhost:8000/predict/analyst?verbose=true&session_id=abc123" \
  -H "Content-Type: application/json" \
  -d '{"text": "Explain neural networks", "temperature": 0.3}'

# DELETE
curl -X DELETE "http://localhost:8000/history/abc123"
```

---

## 10. What to Learn Next

Now that you've built this project, here's the natural progression:

### Immediate next steps
- **Add a real database** — replace in-memory history with PostgreSQL using SQLAlchemy or Tortoise ORM
- **Add authentication** — protect endpoints with API keys using FastAPI's `Security` dependency
- **Add rate limiting** — prevent abuse with `slowapi`
- **Write tests** — use `pytest` + `httpx.AsyncClient` to test all endpoints

### Intermediate
- **Background tasks** — use FastAPI's `BackgroundTasks` for async logging
- **WebSockets** — stream LLM responses token by token instead of waiting for full response
- **Docker** — containerize the app with a `Dockerfile`
- **Environment management** — use `pydantic-settings` for type-safe config

### Advanced
- **Deploy to cloud** — Railway, Render, or Google Cloud Run (all have free tiers)
- **Add caching** — use Redis to cache repeated LLM responses
- **Monitoring** — add logging with `loguru` and metrics with Prometheus
- **CI/CD** — auto-deploy on push using GitHub Actions

### Recommended learning resources
- FastAPI official docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Pydantic docs: [docs.pydantic.dev](https://docs.pydantic.dev)
- Gemini API docs: [ai.google.dev](https://ai.google.dev)
- httpx docs: [www.python-httpx.org](https://www.python-httpx.org)

---

## 🙏 Credits

This guide was built from a real learning conversation while building the Multi-Model AI Playground API project. Every error, fix, concept, and decision documented here was encountered during actual development.

> **For students:** Don't just read — build it yourself. Make the errors. Fix them. That's how it sticks.

---

*Last updated: March 2026*
