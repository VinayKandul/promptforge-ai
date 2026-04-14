"""OpenAI Model Adapter."""
import httpx
from typing import Dict
from .base_adapter import BaseModelAdapter


class OpenAIAdapter(BaseModelAdapter):
    """Adapter for OpenAI models (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model_name", "gpt-4")
        self.base_url = "https://api.openai.com/v1"

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
            "provider": "OpenAI",
            "model": self.model_name,
            "max_tokens": 128000,
            "supports_streaming": True,
        }

    def _create_mock_response(self, prompt: str) -> Dict:
        mock = (
            "## Mock Response (OpenAI API key not configured)\n\n"
            "This is a simulated response. To get real AI responses, "
            "set your `OPENAI_API_KEY` environment variable.\n\n"
            f"**Your optimized prompt was {len(prompt.split())} words long** and would have been "
            f"sent to the `{self.model_name}` model.\n\n"
            "### What would happen with a real API key:\n"
            "1. Your prompt would be sent to OpenAI's servers\n"
            "2. The model would process your structured prompt\n"
            "3. You'd receive a high-quality response optimized by PromptForge\n"
        )
        return self._create_success_response(mock, 0)
