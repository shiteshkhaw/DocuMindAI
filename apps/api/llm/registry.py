import logging
from typing import Dict, Tuple
from llm.base import BaseLLMProvider
from llm.openai import OpenAIProvider
from llm.gemini import GeminiProvider
from llm.groq import GroqProvider

logger = logging.getLogger("documind.llm.registry")

class LLMRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        name = provider_name.lower().strip()
        if name not in self._providers:
            if name == "openai":
                self._providers[name] = OpenAIProvider()
            elif name == "gemini":
                self._providers[name] = GeminiProvider()
            elif name == "groq":
                self._providers[name] = GroqProvider()
            else:
                raise ValueError(f"Unsupported LLM provider: {provider_name}")
        return self._providers[name]

    def register_provider(self, provider_name: str, provider: BaseLLMProvider):
        self._providers[provider_name.lower().strip()] = provider

    def resolve_model_route(self, model_name: str) -> Tuple[str, str]:
        """
        Resolves a user-friendly model name (or configuration model string)
        into a (provider_name, actual_model_name) tuple.
        """
        m = model_name.lower().strip()
        
        # 1. Fallbacks for specific DocuMind model names
        if m == "documind-v3":
            return "openai", "gpt-4o-mini"
        elif m == "deepseek-r1":
            # Map to active Llama 3.3 model on Groq as deepseek-r1 is decommissioned
            return "groq", "llama-3.3-70b-versatile"
        elif m in ("claude-3-5-sonnet", "claude-35"):
            return "openai", "gpt-4o"
            
        # 2. Default mapping tables
        if "gpt-4" in m or "gpt-3.5" in m or "o1" in m:
            return "openai", model_name
        elif "gemini" in m:
            return "gemini", model_name
        elif "llama" in m or "mixtral" in m or "gemma" in m or "deepseek" in m:
            # Route deepseek/llama models via Groq if available
            if "deepseek" in m:
                return "groq", "llama-3.3-70b-versatile"
            return "groq", model_name
            
        # Default fallback
        return "openai", "gpt-4o-mini"

llm_registry = LLMRegistry()
