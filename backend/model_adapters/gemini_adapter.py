"""Gemini Model Adapter."""
import httpx
from typing import Dict
from .base_adapter import BaseModelAdapter


class GeminiAdapter(BaseModelAdapter):
    """Adapter for Google Gemini models."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model_name", "gemini-2.0-flash")

    async def generate(self, prompt: str, **kwargs) -> Dict:
        if not self.is_configured():
            return self._create_mock_response(prompt)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": kwargs.get("temperature", 0.7),
                            "maxOutputTokens": kwargs.get("max_tokens", 2000),
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                return self._create_success_response(content, tokens)
        except Exception as e:
            return self._create_error_response(str(e))

    def get_model_info(self) -> Dict:
        return {
            "provider": "Google",
            "model": self.model_name,
            "max_tokens": 1000000,
            "supports_streaming": True,
        }

    def _create_mock_response(self, prompt: str) -> Dict:
        mock = (
            "## Mock Response (Gemini API key not configured)\n\n"
            "This is a simulated response. Set your `GEMINI_API_KEY` env variable.\n\n"
            f"**Prompt length: {len(prompt.split())} words** → `{self.model_name}`"
        )
        return self._create_success_response(mock, 0)
