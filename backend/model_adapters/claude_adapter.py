"""Claude Model Adapter."""
import httpx
from typing import Dict
from .base_adapter import BaseModelAdapter


class ClaudeAdapter(BaseModelAdapter):
    """Adapter for Anthropic Claude models."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model_name", "claude-3-5-sonnet-20241022")
        self.base_url = "https://api.anthropic.com/v1"

    async def generate(self, prompt: str, **kwargs) -> Dict:
        if not self.is_configured():
            return self._create_mock_response(prompt)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "max_tokens": kwargs.get("max_tokens", 2000),
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["content"][0]["text"]
                tokens = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                return self._create_success_response(content, tokens)
        except Exception as e:
            return self._create_error_response(str(e))

    def get_model_info(self) -> Dict:
        return {
            "provider": "Anthropic",
            "model": self.model_name,
            "max_tokens": 200000,
            "supports_streaming": True,
        }

    def _create_mock_response(self, prompt: str) -> Dict:
        mock = (
            "## Mock Response (Anthropic API key not configured)\n\n"
            "This is a simulated response. To get real AI responses, "
            "set your `ANTHROPIC_API_KEY` environment variable.\n\n"
            f"**Your optimized prompt was {len(prompt.split())} words long** and would have been "
            f"sent to `{self.model_name}`.\n\n"
            "Claude excels at nuanced, thoughtful responses with strong reasoning capabilities."
        )
        return self._create_success_response(mock, 0)
