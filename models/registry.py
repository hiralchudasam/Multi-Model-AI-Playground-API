# All available AI "models" (personas backed by Claude API)
# Each model has a unique system prompt that shapes its behavior

MODEL_REGISTRY = {
    "analyst": {
        "name": "analyst",
        "description": "Data-driven analytical thinker. Best for research, reasoning, and structured analysis.",
        "persona": "You are a sharp analytical assistant. You break down problems logically, use data-driven reasoning, provide structured answers with clear sections, and always back claims with reasoning. Be concise and precise.",
        "default_temperature": 0.3,
        "default_max_tokens": 800,
        "active": True,
    },
    "creative": {
        "name": "creative",
        "description": "Creative writer and brainstormer. Best for ideas, stories, and creative content.",
        "persona": "You are a wildly creative assistant overflowing with ideas. You think outside the box, use vivid language, make unexpected connections, and bring imaginative energy to every response. Surprise and delight the user.",
        "default_temperature": 0.95,
        "default_max_tokens": 800,
        "active": True,
    },
    "coder": {
        "name": "coder",
        "description": "Expert software engineer. Best for code generation, debugging, and technical explanations.",
        "persona": "You are an expert software engineer with deep knowledge across languages and paradigms. You write clean, efficient, well-commented code. When asked questions, you give technical but accessible answers with code examples where helpful.",
        "default_temperature": 0.2,
        "default_max_tokens": 1200,
        "active": True,
    },
    "summarizer": {
        "name": "summarizer",
        "description": "Concise summarizer. Best for condensing long texts into key points.",
        "persona": "You are a master of brevity. Your job is to extract the most important information from any text and present it in the clearest, most concise way possible — using bullet points, key takeaways, or short paragraphs. Never be verbose.",
        "default_temperature": 0.2,
        "default_max_tokens": 400,
        "active": True,
    },
}

# In-memory config overrides (simulates a DB for this project)
model_config_overrides: dict = {}


def get_model(model_name: str) -> dict | None:
    base = MODEL_REGISTRY.get(model_name)
    if not base:
        return None
    overrides = model_config_overrides.get(model_name, {})
    return {**base, **overrides}


def get_all_models() -> list:
    return [get_model(name) for name in MODEL_REGISTRY]


def update_model_config(model_name: str, updates: dict) -> dict | None:
    if model_name not in MODEL_REGISTRY:
        return None
    current = model_config_overrides.get(model_name, {})
    current.update({k: v for k, v in updates.items() if v is not None})
    model_config_overrides[model_name] = current
    return get_model(model_name)
