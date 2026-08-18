import os
from typing import Optional
from app.ai.provider import BaseAIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.gemini_provider import GeminiAIProvider

def get_ai_provider(provider_type: Optional[str] = None) -> BaseAIProvider:
    """
    Factory function returning the configured AI Provider.
    Defaults to GeminiAIProvider if GEMINI_API_KEY is present, else MockAIProvider.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if provider_type == "mock" or not api_key:
        return MockAIProvider()
    return GeminiAIProvider(api_key=api_key)

__all__ = ["BaseAIProvider", "MockAIProvider", "GeminiAIProvider", "get_ai_provider"]
