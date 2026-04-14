"""DeepSeek Model Adapter."""
import httpx
from typing import Dict
from .base_adapter import BaseModelAdapter


class DeepSeekAdapter(BaseModelAdapter):
    """Adapter for DeepSeek models (OpenAI-compatible API)."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model_name", "deepseek-chat")
        self.base_url = "https://api.deepseek.com/v1"

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
            "provider": "DeepSeek",
            "model": self.model_name,
            "max_tokens": 64000,
            "supports_streaming": True,
        }

    def _create_mock_response(self, prompt: str) -> Dict:
        mock = (
            "## Mock Response (DeepSeek API key not configured)\n\n"
            "Set your `DEEPSEEK_API_KEY` env variable for real responses.\n\n"
            f"**Prompt length: {len(prompt.split())} words** → `{self.model_name}`"
        )
        return self._create_success_response(mock, 0)
