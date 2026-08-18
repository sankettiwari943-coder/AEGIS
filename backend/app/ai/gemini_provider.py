import os
import json
import httpx
from typing import Dict, Any, Optional
from app.ai.provider import BaseAIProvider
from app.ai.mock_provider import MockAIProvider
from app.config import settings

class GeminiAIProvider(BaseAIProvider):
    """
    Google Gemini AI Provider utilizing Google Generative Language REST API.
    Gracefully falls back to MockAIProvider if GEMINI_API_KEY is not configured or network fails.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.fallback = MockAIProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instructions:\n{system_prompt}\n\nPlease acknowledge."}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will strictly follow these operational instructions."}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                # Fallback if non-200
                return self.fallback.generate(prompt, system_prompt)
        except Exception:
            return self.fallback.generate(prompt, system_prompt)

    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.generate_structured(prompt, system_prompt)

        # Append structured JSON output instruction
        structured_prompt = (
            f"{prompt}\n\n"
            "CRITICAL: Output your response strictly as valid JSON with the following schema keys:\n"
            "{\n"
            '  "answer": "...",\n'
            '  "direct_answer": "...",\n'
            '  "why_rationale": ["...", "..."],\n'
            '  "facts": ["..."],\n'
            '  "model_estimates": ["..."],\n'
            '  "uncertainties": ["..."],\n'
            '  "recommendations": ["..."],\n'
            '  "confidence": 0.90\n'
            "}"
        )

        raw_text = self.generate(structured_prompt, system_prompt)
        try:
            # Strip possible markdown fences
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            return json.loads(clean_text)
        except Exception:
            return self.fallback.generate_structured(prompt, system_prompt)
