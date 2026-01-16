"""Prompt caching and token-based tracking for cost optimization."""

from typing import Dict, Optional
from datetime import datetime
import hashlib

from pycaching.backends.memory import MemoryBackend
from pycaching.core.backend import Backend
from pycaching.core.types import CacheKey, CacheValue
from pycaching.llm.token_tracker import TokenTracker


class PromptCache:
    """Cache for LLM prompts and responses with token tracking."""

    def __init__(
        self,
        backend: Optional[Backend] = None,
        normalize_prompt: bool = True,
        default_ttl: Optional[float] = None,
    ):
        """
        Initialize prompt cache.

        Args:
            backend: Backend to store cache entries
            normalize_prompt: Whether to normalize prompts before hashing
            default_ttl: Default time-to-live for cache entries
        """
        self.backend = backend or MemoryBackend()
        self.normalize_prompt = normalize_prompt
        self.default_ttl = default_ttl
        self.token_tracker = TokenTracker()

    def _normalize_prompt(self, prompt: str) -> str:
        """Normalize prompt for consistent hashing."""
        if not self.normalize_prompt:
            return prompt

        # Remove extra whitespace, normalize line endings
        import re
        prompt = re.sub(r"\s+", " ", prompt.strip())
        prompt = prompt.replace("\r\n", "\n").replace("\r", "\n")
        return prompt

    def _generate_key(self, prompt: str) -> str:
        """Generate a cache key from a prompt."""
        normalized = self._normalize_prompt(prompt)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(
        self,
        prompt: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[CacheValue]:
        """
        Get a cached response for a prompt.

        Args:
            prompt: The prompt text
            metadata: Optional metadata to include in key

        Returns:
            Cached response if found, None otherwise
        """
        key = self._generate_key(prompt)
        if metadata:
            # Include metadata in key
            import json
            metadata_str = json.dumps(metadata, sort_keys=True)
            key = hashlib.sha256((key + metadata_str).encode("utf-8")).hexdigest()

        response = self.backend.get(key)
        if response is not None:
            self.token_tracker.record_request(0, 0, cached=True)
        else:
            self.token_tracker.record_request(0, 0, cached=False)
        return response

    def set(
        self,
        prompt: str,
        response: CacheValue,
        metadata: Optional[Dict] = None,
        ttl: Optional[float] = None,
    ) -> bool:
        """
        Cache a prompt-response pair.

        Args:
            prompt: The prompt text
            response: The response to cache
            metadata: Optional metadata to include in key
            ttl: Optional time-to-live in seconds

        Returns:
            True if successfully cached
        """
        key = self._generate_key(prompt)
        if metadata:
            import json
            metadata_str = json.dumps(metadata, sort_keys=True)
            key = hashlib.sha256((key + metadata_str).encode("utf-8")).hexdigest()

        effective_ttl = ttl or self.default_ttl
        return self.backend.set(key, response, effective_ttl)

    def delete(self, prompt: str, metadata: Optional[Dict] = None) -> bool:
        """Delete a cached prompt-response pair."""
        key = self._generate_key(prompt)
        if metadata:
            import json
            metadata_str = json.dumps(metadata, sort_keys=True)
            key = hashlib.sha256((key + metadata_str).encode("utf-8")).hexdigest()
        return self.backend.delete(key)

    def clear(self) -> bool:
        """Clear all cached entries."""
        return self.backend.clear()

    def get_token_stats(self) -> Dict[str, any]:
        """Get token usage statistics."""
        return self.token_tracker.get_stats()
