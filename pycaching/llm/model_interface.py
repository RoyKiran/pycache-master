"""Model-agnostic caching layer for different LLM providers."""

from typing import Any, Callable, Dict, Optional, Protocol
from abc import ABC, abstractmethod

from pycaching.llm.prompt_cache import PromptCache
from pycaching.llm.semantic_cache import SemanticCache
from pycaching.llm.token_tracker import TokenTracker


class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    async def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the LLM."""
        ...

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        ...


class LLMCacheInterface:
    """Model-agnostic caching interface for LLM providers."""

    def __init__(
        self,
        provider: LLMProvider,
        use_semantic_cache: bool = False,
        embedding_model_name: Optional[str] = None,
        embedding_device: Optional[str] = None,
        similarity_threshold: float = 0.8,
        cache_ttl: Optional[float] = None,
    ):
        """
        Initialize LLM cache interface.

        Args:
            provider: LLM provider instance
            use_semantic_cache: Whether to use semantic similarity caching
            embedding_model_name: Name of embedding model for semantic cache
            embedding_device: Device for embedding model (cpu, cuda, etc.)
            similarity_threshold: Similarity threshold for semantic cache
            cache_ttl: Time-to-live for cache entries
        """
        self.provider = provider
        self.use_semantic_cache = use_semantic_cache
        self.cache_ttl = cache_ttl

        if use_semantic_cache:
            self.cache = SemanticCache(
                similarity_threshold=similarity_threshold,
                model_name=embedding_model_name,
                device=embedding_device,
            )
        else:
            self.cache = PromptCache(default_ttl=cache_ttl)

        self.token_tracker = TokenTracker()

    async def generate(
        self,
        prompt: str,
        use_cache: bool = True,
        metadata: Optional[Dict] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate a response with caching.

        Args:
            prompt: The prompt text
            use_cache: Whether to use cache
            metadata: Optional metadata for cache key
            **kwargs: Additional arguments for LLM provider

        Returns:
            Generated response
        """
        # Try to get from cache
        if use_cache:
            cached_response = self.cache.get(prompt, metadata)
            if cached_response is not None:
                self.token_tracker.record_request(0, 0, cached=True)
                return cached_response

        # Generate from provider
        response = await self.provider.generate(prompt, **kwargs)

        # Cache the response
        if use_cache:
            if isinstance(self.cache, PromptCache):
                self.cache.set(prompt, response, metadata=metadata, ttl=self.cache_ttl)
            else:
                self.cache.set(prompt, response, ttl=self.cache_ttl)

        # Track tokens
        prompt_tokens = self.provider.count_tokens(prompt)
        response_tokens = self.provider.count_tokens(response)
        self.token_tracker.record_request(
            prompt_tokens,
            response_tokens,
            cached=False,
        )

        return response

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if isinstance(self.cache, PromptCache):
            return self.cache.get_token_stats()
        return {"cache_type": "semantic"}

    def get_token_stats(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        return self.token_tracker.get_stats()

    def clear_cache(self) -> bool:
        """Clear the cache."""
        return self.cache.clear()


# Example provider implementations
class OpenAIProvider:
    """Example OpenAI provider implementation."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate using OpenAI API."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai is required. Install with: pip install openai")

        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.choices[0].message.content

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        try:
            import tiktoken
        except ImportError:
            # Fallback: rough estimation
            return len(text.split()) * 1.3

        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))


class AnthropicProvider:
    """Example Anthropic provider implementation."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate using Anthropic API."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic is required. Install with: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.content[0].text

    def count_tokens(self, text: str) -> int:
        """Count tokens using Anthropic's tokenizer."""
        try:
            import anthropic
        except ImportError:
            # Fallback: rough estimation
            return len(text.split()) * 1.3

        client = anthropic.Anthropic(api_key=self.api_key)
        return client.count_tokens(text)
