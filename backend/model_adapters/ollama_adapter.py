"""Ollama Model Adapter (Local models)."""
import httpx
from typing import Dict
from .base_adapter import BaseModelAdapter


class OllamaAdapter(BaseModelAdapter):
    """Adapter for local models via Ollama."""

    def __init__(self, api_key: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model_name", "llama3")
        self.base_url = kwargs.get("base_url", "http://localhost:11434")

    def is_configured(self) -> bool:
        """Ollama doesn't need an API key."""
        return True

    async def generate(self, prompt: str, **kwargs) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": kwargs.get("temperature", 0.7),
                            "num_predict": kwargs.get("max_tokens", 2000),
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("response", "")
                tokens = data.get("eval_count", 0)
                return self._create_success_response(content, tokens)
        except httpx.ConnectError:
            return self._create_error_response(
                "Cannot connect to Ollama. Make sure Ollama is running locally "
                "on port 11434. Start it with: `ollama serve`"
            )
        except Exception as e:
            return self._create_error_response(str(e))

    def get_model_info(self) -> Dict:
        return {
            "provider": "Ollama (Local)",
            "model": self.model_name,
            "max_tokens": -1,
            "supports_streaming": True,
        }
