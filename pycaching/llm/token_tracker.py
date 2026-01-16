"""Token tracking for LLM cost optimization."""

from typing import Dict, Optional
from datetime import datetime


class TokenTracker:
    """Track token usage and costs for LLM operations."""

    def __init__(self):
        """Initialize token tracker."""
        self.total_tokens: int = 0
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cost: float = 0.0
        self.requests: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self._history: list[Dict] = []

    def record_request(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cost_per_1k_tokens: float = 0.002,
        cached: bool = False,
        model: Optional[str] = None,
    ) -> None:
        """
        Record a token usage.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost_per_1k_tokens: Cost per 1000 tokens
            cached: Whether this was a cache hit
            model: Optional model name
        """
        self.requests += 1
        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.total_tokens += prompt_tokens + completion_tokens

            # Calculate cost
            total_tokens = prompt_tokens + completion_tokens
            cost = (total_tokens / 1000.0) * cost_per_1k_tokens
            self.total_cost += cost

            # Record in history
            self._history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
                "model": model,
            })

    def get_stats(self) -> Dict[str, any]:
        """Get token usage statistics."""
        hit_rate = (
            self.cache_hits / self.requests if self.requests > 0 else 0.0
        )
        estimated_savings = 0.0
        if self.cache_misses > 0:
            avg_cost_per_request = self.total_cost / self.cache_misses
            estimated_savings = self.cache_hits * avg_cost_per_request

        return {
            "total_requests": self.requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "total_tokens": self.total_tokens,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_cost": self.total_cost,
            "estimated_savings": estimated_savings,
        }

    def get_history(self, limit: Optional[int] = None) -> list[Dict]:
        """Get request history."""
        if limit is None:
            return self._history.copy()
        return self._history[-limit:]

    def reset(self) -> None:
        """Reset all statistics."""
        self.total_tokens = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self._history.clear()
