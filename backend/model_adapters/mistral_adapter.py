"""Mistral Model Adapter."""
import httpx
from typing import Dict
from .base_adapter import BaseModelAdapter


class MistralAdapter(BaseModelAdapter):
    """Adapter for Mistral AI models."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model_name", "mistral-large-latest")
        self.base_url = "https://api.mistral.ai/v1"

    async def generate(self, prompt: str, **kwargs) -> Dict:
        if not self.is_configured():
            return self._create_mock_response(prompt)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 2000),
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return self._create_success_response(content, tokens)
        except Exception as e:
            return self._create_error_response(str(e))

    def get_model_info(self) -> Dict:
        return {
            "provider": "Mistral AI",
            "model": self.model_name,
            "max_tokens": 32000,
            "supports_streaming": True,
        }

    def _create_mock_response(self, prompt: str) -> Dict:
        mock = (
            "## Mock Response (Mistral API key not configured)\n\n"
            "Set your `MISTRAL_API_KEY` env variable for real responses.\n\n"
            f"**Prompt length: {len(prompt.split())} words** → `{self.model_name}`"
        )
        return self._create_success_response(mock, 0)
