"""Semantic similarity-based caching for LLM prompts."""

from typing import Dict, List, Optional, Tuple
import numpy as np

from pycaching.backends.memory import MemoryBackend
from pycaching.core.backend import Backend
from pycaching.core.types import CacheKey, CacheValue
from pycaching.llm.embedding import EmbeddingGenerator, SimilarityCalculator


class SemanticCache:
    """Cache that uses semantic similarity to find similar prompts."""

    def __init__(
        self,
        backend: Optional[Backend] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        similarity_threshold: float = 0.8,
        similarity_method: str = "cosine",
    ):
        """
        Initialize semantic cache.

        Args:
            backend: Backend to store cache entries (defaults to MemoryBackend)
            embedding_generator: Embedding generator instance (optional if model_name provided)
            model_name: Name of the embedding model (e.g., 'sentence-transformers/all-MiniLM-L6-v2')
            device: Device to run the model on (cpu, cuda, etc.)
            similarity_threshold: Minimum similarity score to consider a match
            similarity_method: Similarity calculation method ('cosine' or 'euclidean')
        """
        self.backend = backend or MemoryBackend()
        
        # Create embedding generator if not provided
        if embedding_generator is None:
            if model_name is None:
                # Use default model if nothing specified
                model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embedding_generator = EmbeddingGenerator(
                model_name=model_name,
                device=device,
            )
        else:
            self.embedding_generator = embedding_generator
            
        self.similarity_threshold = similarity_threshold
        self.similarity_method = similarity_method
        self._embeddings: Dict[str, np.ndarray] = {}  # key -> embedding
        self._prompts: Dict[str, str] = {}  # key -> original prompt

    def _generate_key(self, prompt: str) -> str:
        """Generate a cache key for a prompt."""
        import hashlib
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]

    def get(self, prompt: str) -> Optional[CacheValue]:
        """
        Get a cached response for a prompt using semantic similarity.

        Args:
            prompt: The prompt to search for

        Returns:
            Cached response if similar prompt found, None otherwise
        """
        # Generate embedding for the query prompt
        query_embedding = self.embedding_generator.generate_single(prompt)

        # Find most similar cached prompt
        if not self._embeddings:
            return None

        # Calculate similarities
        candidates = list(self._embeddings.items())
        similarities = []
        for key, cached_embedding in candidates:
            score, is_similar = SimilarityCalculator.similarity_score(
                query_embedding,
                cached_embedding,
                method=self.similarity_method,
                threshold=self.similarity_threshold,
            )
            if is_similar:
                similarities.append((key, score))

        if not similarities:
            return None

        # Get the most similar
        similarities.sort(key=lambda x: x[1], reverse=True)
        best_key = similarities[0][0]

        # Return cached response
        return self.backend.get(best_key)

    def set(self, prompt: str, response: CacheValue, ttl: Optional[float] = None) -> bool:
        """
        Cache a prompt-response pair.

        Args:
            prompt: The prompt text
            response: The response to cache
            ttl: Optional time-to-live in seconds

        Returns:
            True if successfully cached
        """
        key = self._generate_key(prompt)

        # Generate and store embedding
        embedding = self.embedding_generator.generate_single(prompt)
        self._embeddings[key] = embedding
        self._prompts[key] = prompt

        # Store response in backend
        return self.backend.set(key, response, ttl)

    def delete(self, prompt: str) -> bool:
        """Delete a cached prompt-response pair."""
        key = self._generate_key(prompt)
        self._embeddings.pop(key, None)
        self._prompts.pop(key, None)
        return self.backend.delete(key)

    def clear(self) -> bool:
        """Clear all cached entries."""
        self._embeddings.clear()
        self._prompts.clear()
        return self.backend.clear()

    def find_similar(
        self, prompt: str, top_k: int = 5
    ) -> List[Tuple[str, float, CacheValue]]:
        """
        Find similar prompts and their cached responses.

        Args:
            prompt: Query prompt
            top_k: Number of results to return

        Returns:
            List of tuples (prompt, similarity_score, response)
        """
        query_embedding = self.embedding_generator.generate_single(prompt)

        if not self._embeddings:
            return []

        # Calculate similarities for all cached prompts
        similarities = []
        for key, cached_embedding in self._embeddings.items():
            score = SimilarityCalculator.cosine_similarity(query_embedding, cached_embedding)
            similarities.append((key, score))

        # Sort and get top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = []

        for key, score in similarities[:top_k]:
            response = self.backend.get(key)
            original_prompt = self._prompts.get(key, "")
            results.append((original_prompt, score, response))

        return results
