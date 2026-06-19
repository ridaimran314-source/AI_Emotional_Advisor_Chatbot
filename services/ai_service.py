"""Configurable AI provider service for emotional advisor responses."""

import os
import re

import requests

SYSTEM_PROMPT = """You are a calm, kind, and practical emotional support advisor.
Your job is to listen, understand the user's mood, and give safe general advice.
You are not a doctor, therapist, or medical professional.
Do not diagnose mental health conditions.
Do not prescribe medicine.
If the user mentions self-harm, suicide, or harming others, respond with immediate safety guidance and encourage contacting emergency services or a trusted person.
Keep responses short, human, caring, and practical.
Ask one gentle follow-up question when needed.

After your response, on a new line, output exactly one line in this format:
MOOD: <one of sad, stressed, anxious, angry, lonely, confused, happy, neutral>"""

VALID_MOODS = {
    "sad",
    "stressed",
    "anxious",
    "angry",
    "lonely",
    "confused",
    "happy",
    "neutral",
}


class AIServiceError(Exception):
    """Raised when the AI provider returns an error."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _parse_mood_from_response(text: str) -> tuple[str, str]:
    """Extract mood tag from AI response and return (reply, mood)."""
    match = re.search(r"MOOD:\s*(\w+)", text, re.IGNORECASE)
    if match:
        mood = match.group(1).lower()
        reply = re.sub(r"\n*MOOD:\s*\w+\s*$", "", text, flags=re.IGNORECASE).strip()
        if mood not in VALID_MOODS:
            mood = "neutral"
        return reply, mood
    return text.strip(), "neutral"


def _build_user_prompt(message: str, selected_mood: str | None) -> str:
    parts = [f"User message: {message}"]
    if selected_mood:
        parts.append(f"The user selected their mood as: {selected_mood}")
    return "\n".join(parts)


def _call_groq(api_key: str, model: str, user_prompt: str) -> str:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 512,
        },
        timeout=30,
    )
    if response.status_code == 401:
        raise AIServiceError("Invalid API key. Please check your configuration.", 503)
    if not response.ok:
        raise AIServiceError("The AI service is temporarily unavailable. Please try again later.")
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_gemini(api_key: str, model: str, user_prompt: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512},
        },
        timeout=30,
    )
    if response.status_code in (401, 403):
        raise AIServiceError("Invalid API key. Please check your configuration.", 503)
    if not response.ok:
        raise AIServiceError("The AI service is temporarily unavailable. Please try again later.")
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_openrouter(api_key: str, model: str, user_prompt: str) -> str:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": os.getenv("APP_NAME", "AI Emotional Advisor"),
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 512,
        },
        timeout=60,
    )
    if response.status_code == 401:
        raise AIServiceError("Invalid API key. Please check your configuration.", 503)
    if not response.ok:
        raise AIServiceError("The AI service is temporarily unavailable. Please try again later.")
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_huggingface(api_key: str, model: str, user_prompt: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{model}"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
            "parameters": {"max_new_tokens": 512, "temperature": 0.7, "return_full_text": False},
        },
        timeout=60,
    )
    if response.status_code == 401:
        raise AIServiceError("Invalid API key. Please check your configuration.", 503)
    if not response.ok:
        raise AIServiceError("The AI service is temporarily unavailable. Please try again later.")
    data = response.json()
    if isinstance(data, list):
        return data[0].get("generated_text", "")
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    raise AIServiceError("Unexpected response from AI service.")


PROVIDERS = {
    "groq": _call_groq,
    "gemini": _call_gemini,
    "openrouter": _call_openrouter,
    "huggingface": _call_huggingface,
}


def get_advisor_response(message: str, selected_mood: str | None = None) -> tuple[str, str]:
    """
    Call the configured AI provider and return (reply, detected_mood).
    Raises AIServiceError on configuration or API failures.
    """
    provider = os.getenv("AI_PROVIDER", "groq").lower().strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "llama-3.1-8b-instant").strip()

    if not api_key or api_key in ("your_api_key_here", "your_groq_api_key_here"):
        raise AIServiceError(
            "AI service is not configured. Set AI_API_KEY in .env and save the file.",
            503,
        )

    if provider not in PROVIDERS:
        raise AIServiceError(
            f"Unknown AI provider '{provider}'. Check AI_PROVIDER in your configuration.",
            503,
        )

    user_prompt = _build_user_prompt(message, selected_mood)
    raw_response = PROVIDERS[provider](api_key, model, user_prompt)
    return _parse_mood_from_response(raw_response)
