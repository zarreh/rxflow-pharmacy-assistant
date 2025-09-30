"""
Centralized LLM management for RxFlow Pharmacy Assistant
Provides factory pattern for different LLM providers with easy switching
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Union

from langchain.schema.language_model import BaseLanguageModel
from langchain_ollama import ChatOllama

# Optional imports for additional providers (install as needed)
try:
    from langchain_openai import ChatOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_anthropic import ChatAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from rxflow.config.settings import get_settings
from rxflow.utils.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class LLMConfig:
    """Configuration for LLM instances"""

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
        **kwargs: Any,
    ):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.kwargs = kwargs


class BaseLLMFactory(ABC):
    """Abstract base for LLM factories"""

    @abstractmethod
    def create_llm(self, config: LLMConfig) -> BaseLanguageModel:
        """Create an LLM instance"""
        pass


class OllamaFactory(BaseLLMFactory):
    """Factory for Ollama LLM instances"""

    def create_llm(self, config: LLMConfig) -> ChatOllama:
        settings = get_settings()

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=config.model,
            temperature=config.temperature,
            **config.kwargs,
        )


class OpenAIFactory(BaseLLMFactory):
    """Factory for OpenAI LLM instances"""

    def create_llm(self, config: LLMConfig) -> BaseLanguageModel:
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI not available. Install with: pip install langchain-openai"
            )

        settings = get_settings()

        # Handle OpenAI parameters
        params = {
            "model": config.model,
            "temperature": config.temperature,
            **config.kwargs,
        }

        # Add API key from settings if available
        if settings.openai_api_key:
            params["api_key"] = settings.openai_api_key

        if config.max_tokens is not None:
            params["max_tokens"] = config.max_tokens

        return ChatOpenAI(**params)


class AnthropicFactory(BaseLLMFactory):
    """Factory for Anthropic LLM instances"""

    def create_llm(self, config: LLMConfig) -> BaseLanguageModel:
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic not available. Install with: pip install langchain-anthropic"
            )

        # Anthropic requires max_tokens to be set
        max_tokens = config.max_tokens or 1000
        return ChatAnthropic(
            model_name=config.model,
            temperature=config.temperature,
            max_tokens_to_sample=max_tokens,
            **config.kwargs,
        )


class GeminiFactory(BaseLLMFactory):
    """Factory for Google Gemini LLM instances"""

    def create_llm(self, config: LLMConfig) -> BaseLanguageModel:
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Gemini not available. Install with: pip install langchain-google-genai"
            )

        # Handle None max_tokens for Gemini
        max_tokens = config.max_tokens or 1000
        return ChatGoogleGenerativeAI(
            model=config.model,
            temperature=config.temperature,
            max_output_tokens=max_tokens,
            **config.kwargs,
        )


class LLMManager:
    """Centralized LLM management with caching and easy provider switching"""

    _instance = None
    _llm_cache: Dict[str, BaseLanguageModel] = {}

    def __new__(cls) -> "LLMManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "initialized"):
            self.factories = {
                LLMProvider.OLLAMA: OllamaFactory(),
                LLMProvider.OPENAI: OpenAIFactory(),
                LLMProvider.ANTHROPIC: AnthropicFactory(),
                LLMProvider.GEMINI: GeminiFactory(),
            }
            self.default_provider: Optional[LLMProvider] = None  # Will be set by settings
            self.initialized = True

    def get_llm(
        self,
        provider: Optional[Union[str, LLMProvider]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> BaseLanguageModel:
        """
        Get an LLM instance with caching

        Args:
            provider: LLM provider (defaults to settings)
            model: Model name (defaults to settings)
            temperature: Model temperature
            **kwargs: Additional model parameters

        Returns:
            Configured LLM instance
        """
        settings = get_settings()

        # Use defaults from settings if not provided
        if provider is None:
            # Use switched provider if available, otherwise get from settings
            if hasattr(self, "default_provider") and self.default_provider:
                provider = self.default_provider
            else:
                default_provider = getattr(settings, "default_llm_provider", "openai")
                provider = LLMProvider(default_provider.lower())
        elif isinstance(provider, str):
            provider = LLMProvider(provider.lower())

        if model is None:
            if provider == LLMProvider.OLLAMA:
                model = settings.ollama_model
            elif provider == LLMProvider.OPENAI:
                model = getattr(settings, "openai_model", "gpt-4o-mini")
            elif provider == LLMProvider.ANTHROPIC:
                model = "claude-3-haiku-20240307"
            elif provider == LLMProvider.GEMINI:
                model = "gemini-1.5-flash"
            else:
                model = "gpt-4o-mini"  # Fallback default

        # Ensure model is never None
        if model is None:
            model = "gpt-4o-mini"

        # Create cache key
        cache_key = f"{provider.value}:{model}:{temperature}:{hash(str(kwargs))}"

        # Return cached instance if available
        if cache_key in self._llm_cache:
            logger.debug(f"Using cached LLM: {cache_key}")
            return self._llm_cache[cache_key]

        # Create new LLM instance
        logger.info(f"Creating new LLM: {provider.value}/{model}")

        config = LLMConfig(
            provider=provider, model=model, temperature=temperature, **kwargs
        )

        factory = self.factories.get(provider)
        if not factory:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        try:
            llm = factory.create_llm(config)
            self._llm_cache[cache_key] = llm
            return llm

        except Exception as e:
            logger.error(f"Failed to create LLM {provider.value}/{model}: {e}")
            raise

    def get_conversational_llm(self) -> BaseLanguageModel:
        """Get LLM optimized for conversational interactions"""
        return self.get_llm(
            temperature=0.8,  # More creative for conversations
            max_tokens=500,  # Reasonable response length
            streaming=False,  # For now, disable streaming
        )

    def get_analytical_llm(self) -> BaseLanguageModel:
        """Get LLM optimized for analytical tasks"""
        return self.get_llm(
            temperature=0.3,  # More deterministic for analysis
            max_tokens=200,  # Concise analytical responses
            streaming=False,
        )

    def get_tool_llm(self) -> BaseLanguageModel:
        """Get LLM optimized for tool usage and function calling"""
        return self.get_llm(
            temperature=0.1,  # Very deterministic for tool calls
            max_tokens=300,  # Enough for tool reasoning
            streaming=False,
        )

    def clear_cache(self) -> None:
        """Clear the LLM cache"""
        logger.info("Clearing LLM cache")
        self._llm_cache.clear()

    def switch_provider(self, provider: Union[str, LLMProvider]) -> None:
        """Switch the default LLM provider"""
        if isinstance(provider, str):
            provider = LLMProvider(provider.lower())

        logger.info(f"Switching to LLM provider: {provider.value}")
        self.default_provider = provider
        self.clear_cache()

    def list_available_providers(self) -> list[str]:
        """List all available LLM providers"""
        return [provider.value for provider in self.factories.keys()]


# Global LLM manager instance
llm_manager = LLMManager()


# Convenience functions for easy access
def get_llm(**kwargs: Any) -> BaseLanguageModel:
    """Get a standard LLM instance"""
    return llm_manager.get_llm(**kwargs)


def get_conversational_llm() -> BaseLanguageModel:
    """Get LLM optimized for conversations"""
    return llm_manager.get_conversational_llm()


def get_analytical_llm() -> BaseLanguageModel:
    """Get LLM optimized for analysis"""
    return llm_manager.get_analytical_llm()


def get_tool_llm() -> BaseLanguageModel:
    """Get LLM optimized for tool usage"""
    return llm_manager.get_tool_llm()


def switch_llm_provider(provider: str) -> None:
    """Switch LLM provider globally"""
    llm_manager.switch_provider(provider)


def switch_to_openai() -> None:
    """Quick switch to OpenAI GPT-4 Mini"""
    switch_llm_provider("openai")
    logger.info("Switched to OpenAI GPT-4 Mini")


def switch_to_ollama() -> None:
    """Quick switch to Ollama (local)"""
    switch_llm_provider("ollama")
    logger.info("Switched to Ollama Llama 3.2")


def get_current_provider() -> str:
    """Get the current LLM provider"""
    settings = get_settings()
    return getattr(settings, "default_llm_provider", "openai")


def clear_llm_cache() -> None:
    """Clear global LLM cache"""
    llm_manager.clear_cache()
