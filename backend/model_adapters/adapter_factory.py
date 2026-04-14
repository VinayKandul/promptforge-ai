"""Model Adapter Factory.

Factory pattern to get the appropriate adapter based on model selection.
Supports per-user API keys passed at call time.
"""
from typing import Dict, Optional
from .base_adapter import BaseModelAdapter
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter
from .gemini_adapter import GeminiAdapter
from .mistral_adapter import MistralAdapter
from .deepseek_adapter import DeepSeekAdapter
from .ollama_adapter import OllamaAdapter
from config import OLLAMA_BASE_URL


# Available models registry
AVAILABLE_MODELS = {
    "openai": {
        "provider": "OpenAI",
        "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default": "gpt-4",
        "icon": "🟢",
    },
    "claude": {
        "provider": "Anthropic",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        "default": "claude-3-5-sonnet-20241022",
        "icon": "🟠",
    },
    "gemini": {
        "provider": "Google",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro"],
        "default": "gemini-2.0-flash",
        "icon": "🔵",
    },
    "mistral": {
        "provider": "Mistral AI",
        "models": ["mistral-large-latest", "mistral-medium-latest"],
        "default": "mistral-large-latest",
        "icon": "🟡",
    },
    "deepseek": {
        "provider": "DeepSeek",
        "models": ["deepseek-chat", "deepseek-coder"],
        "default": "deepseek-chat",
        "icon": "🟣",
    },
    "ollama": {
        "provider": "Ollama (Local)",
        "models": ["llama3", "mixtral", "codellama", "mistral"],
        "default": "llama3",
        "icon": "⚫",
    },
}

# Maps provider names to the key name expected by each adapter
PROVIDER_KEY_MAP = {
    "openai": "openai",
    "claude": "claude",
    "gemini": "gemini",
    "mistral": "mistral",
    "deepseek": "deepseek",
    "ollama": "ollama",
}


def get_adapter(
    provider: str,
    model_name: Optional[str] = None,
    user_api_keys: Optional[Dict[str, str]] = None,
) -> BaseModelAdapter:
    """
    Get the appropriate model adapter for the given provider.

    Args:
        provider: Model provider key (e.g., "openai", "claude")
        model_name: Specific model name (uses default if None)
        user_api_keys: Dict mapping provider → decrypted API key from user settings

    Returns:
        Configured BaseModelAdapter instance
    """
    provider = provider.lower().strip()
    if user_api_keys is None:
        user_api_keys = {}

    if provider not in AVAILABLE_MODELS:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available: {', '.join(AVAILABLE_MODELS.keys())}"
        )

    if model_name is None:
        model_name = AVAILABLE_MODELS[provider]["default"]

    # Retrieve user's API key for this provider (empty string triggers mock)
    api_key = user_api_keys.get(provider, "")

    adapters = {
        "openai": lambda: OpenAIAdapter(
            api_key=api_key, model_name=model_name
        ),
        "claude": lambda: ClaudeAdapter(
            api_key=api_key, model_name=model_name
        ),
        "gemini": lambda: GeminiAdapter(
            api_key=api_key, model_name=model_name
        ),
        "mistral": lambda: MistralAdapter(
            api_key=api_key, model_name=model_name
        ),
        "deepseek": lambda: DeepSeekAdapter(
            api_key=api_key, model_name=model_name
        ),
        "ollama": lambda: OllamaAdapter(
            base_url=OLLAMA_BASE_URL, model_name=model_name
        ),
    }

    return adapters[provider]()


def get_available_models(user_api_keys: Optional[Dict[str, str]] = None) -> Dict:
    """Return the full list of available models and their configuration status."""
    if user_api_keys is None:
        user_api_keys = {}

    result = {}
    for provider_key, info in AVAILABLE_MODELS.items():
        has_key = bool(user_api_keys.get(provider_key)) or provider_key == "ollama"
        result[provider_key] = {
            **info,
            "configured": has_key,
            "status": "ready" if has_key else "api_key_required",
        }

    return result
