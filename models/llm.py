import os
import httpx
from typing import Optional

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


async def call_gemini(
    user_text: str,
    system_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
    system_hint: Optional[str] = None,
) -> tuple[str, int]:
    """
    Call Gemini API and return (response_text, tokens_used).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    full_system = system_prompt
    if system_hint:
        full_system += f"\n\nAdditional instruction: {system_hint}"

    payload = {
        "system_instruction": {
            "parts": [{"text": full_system}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_text}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
    }

    url = f"{GEMINI_API_URL}?key={api_key}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    tokens = data.get("usageMetadata", {}).get("candidatesTokenCount", 0)
    return text, tokens
