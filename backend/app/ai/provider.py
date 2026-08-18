from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAIProvider(ABC):
    """
    Abstract Base Class for AI Model Providers (Gemini, Mock, etc.).
    Decouples core AEGIS services from direct LLM vendor SDK dependencies.
    """
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates plain text response."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generates structured dictionary response."""
        pass
