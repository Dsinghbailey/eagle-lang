"""Hardcoded provider configurations for Eagle."""

from typing import Dict, List, Any


# Hardcoded provider configurations
PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "api_key_env": "OPENAI_API_KEY",
        "description": "OpenAI's GPT models"
    },
    "claude": {
        "name": "Claude/Anthropic", 
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        "api_key_env": "ANTHROPIC_API_KEY",
        "description": "Anthropic's Claude models"
    },
    "gemini": {
        "name": "Google Gemini",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
        "api_key_env": "GOOGLE_API_KEY",
        "description": "Google's Gemini models"
    },
    "openrouter": {
        "name": "OpenRouter",
        "models": [
            "anthropic/claude-3.5-sonnet",
            "google/gemini-pro-1.5", 
            "openai/gpt-4o",
            "meta-llama/llama-3.1-405b-instruct",
            "anthropic/claude-3-opus"
        ],
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "description": "Access to multiple models via OpenRouter"
    }
}


def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for a specific provider."""
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available providers: {list(PROVIDERS.keys())}")
    return PROVIDERS[provider]


def get_available_providers() -> List[str]:
    """Get list of available provider names."""
    return list(PROVIDERS.keys())


def get_provider_models(provider: str) -> List[str]:
    """Get available models for a provider."""
    return get_provider_config(provider)["models"]


def get_provider_api_key_env(provider: str) -> str:
    """Get the environment variable name for a provider's API key."""
    return get_provider_config(provider)["api_key_env"]


def is_valid_provider(provider: str) -> bool:
    """Check if a provider is valid."""
    return provider in PROVIDERS


def is_valid_model_for_provider(provider: str, model: str) -> bool:
    """Check if a model is valid for a provider."""
    if not is_valid_provider(provider):
        return False
    return model in get_provider_models(provider)