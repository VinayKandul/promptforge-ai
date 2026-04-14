"""Base Model Adapter.

Abstract base class defining the interface for all AI model adapters.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseModelAdapter(ABC):
    """Abstract base class for AI model adapters."""

    def __init__(self, api_key: str = "", **kwargs):
        self.api_key = api_key
        self.model_name = kwargs.get("model_name", "")
        self.base_url = kwargs.get("base_url", "")

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict:
        """
        Generate a response from the AI model.

        Args:
            prompt: The optimized prompt to send
            **kwargs: Additional model-specific parameters

        Returns:
            Dict with keys: response, model, tokens_used, success, error
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        """Return information about the model."""
        pass

    def is_configured(self) -> bool:
        """Check if the adapter has valid configuration."""
        return bool(self.api_key)

    def _create_error_response(self, error: str) -> Dict:
        """Create a standardized error response."""
        return {
            "response": "",
            "model": self.model_name,
            "tokens_used": 0,
            "success": False,
            "error": error,
        }

    def _create_success_response(self, response: str, tokens: int = 0) -> Dict:
        """Create a standardized success response."""
        return {
            "response": response,
            "model": self.model_name,
            "tokens_used": tokens,
            "success": True,
            "error": None,
        }
