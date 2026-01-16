"""Embedding generation and semantic similarity calculation for LLM caching."""

from typing import Any, Callable, Dict, List, Optional, Protocol, Union
import numpy as np

from pycaching.core.exceptions import CacheError


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    def generate(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text."""
        ...


class EmbeddingGenerator:
    """Generate embeddings for text using various models and providers."""

    def __init__(
        self,
        provider: str = "huggingface",  # huggingface, ollama, openai, azure, aws, custom
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        custom_provider: Optional[Callable[[Union[str, List[str]]], np.ndarray]] = None,
        **kwargs: Any,
    ):
        """
        Initialize the embedding generator.

        Args:
            provider: Provider type ('huggingface', 'ollama', 'openai', 'azure', 'aws', 'custom')
            model_name: Name of the model (provider-specific)
            device: Device to run the model on (cpu, cuda, etc.) - for local models
            api_key: API key for cloud providers
            api_base: API base URL (for Azure OpenAI or Ollama)
            custom_provider: Custom provider function (for 'custom' provider)
            **kwargs: Additional provider-specific arguments
                - For Ollama: base_url (default: http://localhost:11434)
                - For HuggingFace: trust_remote_code, etc.
        """
        self.provider_type = provider.lower()
        self.model_name = model_name
        self.device = device
        self.api_key = api_key
        self.api_base = api_base
        self.custom_provider = custom_provider
        self.kwargs = kwargs
        self._provider = None

    def _load_provider(self) -> EmbeddingProvider:
        """Lazy load the embedding provider."""
        if self._provider is not None:
            return self._provider

        if self.provider_type == "huggingface":
            self._provider = self._create_huggingface_provider()
        elif self.provider_type == "ollama":
            self._provider = self._create_ollama_provider()
        elif self.provider_type == "openai":
            self._provider = self._create_openai_provider()
        elif self.provider_type == "azure":
            self._provider = self._create_azure_provider()
        elif self.provider_type == "aws":
            self._provider = self._create_aws_provider()
        elif self.provider_type == "custom":
            self._provider = self._create_custom_provider()
        else:
            raise ValueError(
                f"Unknown provider: {self.provider_type}. "
                "Supported: huggingface, ollama, openai, azure, aws, custom"
            )

        return self._provider

    def _create_huggingface_provider(self) -> EmbeddingProvider:
        """Create HuggingFace sentence-transformers provider."""
        model_name = self.model_name or "sentence-transformers/all-MiniLM-L6-v2"
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(model_name, device=self.device)
            
            class HuggingFaceProvider:
                def __init__(self, model):
                    self.model = model
                
                def generate(self, text: Union[str, List[str]]) -> np.ndarray:
                    return self.model.encode(text, convert_to_numpy=True)
            
            return HuggingFaceProvider(model)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for HuggingFace provider. "
                "Install with: pip install sentence-transformers"
            )

    def _create_ollama_provider(self) -> EmbeddingProvider:
        """Create Ollama embeddings provider (on-premise/local)."""
        model_name = self.model_name or "nomic-embed-text"
        base_url = self.api_base or self.kwargs.get("base_url", "http://localhost:11434")
        
        try:
            import requests
        except ImportError:
            raise ImportError("requests is required for Ollama provider. Install with: pip install requests")
        
        class OllamaProvider:
            def __init__(self, model_name: str, base_url: str):
                self.model_name = model_name
                self.base_url = base_url.rstrip("/")
            
            def generate(self, text: Union[str, List[str]]) -> np.ndarray:
                texts = [text] if isinstance(text, str) else text
                embeddings = []
                
                for txt in texts:
                    response = requests.post(
                        f"{self.base_url}/api/embeddings",
                        json={
                            "model": self.model_name,
                            "prompt": txt,
                        },
                        timeout=30,
                    )
                    response.raise_for_status()
                    result = response.json()
                    embeddings.append(result.get("embedding", []))
                
                result = np.array(embeddings, dtype=np.float32)
                return result[0] if isinstance(text, str) else result
        
        return OllamaProvider(model_name, base_url)

    def _create_openai_provider(self) -> EmbeddingProvider:
        """Create OpenAI embeddings provider."""
        model_name = self.model_name or "text-embedding-ada-002"
        api_key = self.api_key
        
        if not api_key:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is required. Provide api_key or set OPENAI_API_KEY env var.")

        try:
            import openai
        except ImportError:
            raise ImportError("openai is required for OpenAI provider. Install with: pip install openai")

        client = openai.OpenAI(api_key=api_key, **self.kwargs)
        
        class OpenAIProvider:
            def __init__(self, client, model_name):
                self.client = client
                self.model_name = model_name
            
            def generate(self, text: Union[str, List[str]]) -> np.ndarray:
                texts = [text] if isinstance(text, str) else text
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=texts,
                )
                embeddings = [item.embedding for item in response.data]
                result = np.array(embeddings)
                return result[0] if isinstance(text, str) else result
        
        return OpenAIProvider(client, model_name)

    def _create_azure_provider(self) -> EmbeddingProvider:
        """Create Azure OpenAI embeddings provider."""
        model_name = self.model_name or "text-embedding-ada-002"
        api_key = self.api_key
        api_base = self.api_base
        
        if not api_key:
            import os
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Azure OpenAI API key is required. Provide api_key or set AZURE_OPENAI_API_KEY env var.")
        
        if not api_base:
            import os
            api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
            if not api_base:
                raise ValueError("Azure OpenAI endpoint is required. Provide api_base or set AZURE_OPENAI_ENDPOINT env var.")

        try:
            import openai
        except ImportError:
            raise ImportError("openai is required for Azure provider. Install with: pip install openai")

        client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=api_base,
            api_version=self.kwargs.get("api_version", "2023-05-15"),
        )
        
        class AzureProvider:
            def __init__(self, client, model_name):
                self.client = client
                self.model_name = model_name
            
            def generate(self, text: Union[str, List[str]]) -> np.ndarray:
                texts = [text] if isinstance(text, str) else text
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=texts,
                )
                embeddings = [item.embedding for item in response.data]
                result = np.array(embeddings)
                return result[0] if isinstance(text, str) else result
        
        return AzureProvider(client, model_name)

    def _create_aws_provider(self) -> EmbeddingProvider:
        """Create AWS Bedrock embeddings provider."""
        model_name = self.model_name or "amazon.titan-embed-text-v1"
        region = self.kwargs.get("region", "us-east-1")
        
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for AWS provider. Install with: pip install boto3")

        bedrock_runtime = boto3.client(
            "bedrock-runtime",
            region_name=region,
            **{k: v for k, v in self.kwargs.items() if k != "region"},
        )
        
        class AWSProvider:
            def __init__(self, client, model_name):
                self.client = client
                self.model_name = model_name
            
            def generate(self, text: Union[str, List[str]]) -> np.ndarray:
                texts = [text] if isinstance(text, str) else text
                embeddings = []
                
                for txt in texts:
                    import json
                    body = json.dumps({"inputText": txt})
                    response = self.client.invoke_model(
                        modelId=self.model_name,
                        body=body,
                        contentType="application/json",
                        accept="application/json",
                    )
                    result = json.loads(response["body"].read())
                    embeddings.append(result.get("embedding", []))
                
                result = np.array(embeddings)
                return result[0] if isinstance(text, str) else result
        
        return AWSProvider(bedrock_runtime, model_name)

    def _create_custom_provider(self) -> EmbeddingProvider:
        """Create custom provider from function."""
        if self.custom_provider is None:
            raise ValueError("custom_provider function is required for 'custom' provider type")
        
        class CustomProvider:
            def __init__(self, func):
                self.func = func
            
            def generate(self, text: Union[str, List[str]]) -> np.ndarray:
                result = self.func(text)
                if not isinstance(result, np.ndarray):
                    result = np.array(result)
                return result
        
        return CustomProvider(self.custom_provider)

    def generate(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text.

        Args:
            text: Single text string or list of text strings

        Returns:
            Numpy array of embeddings (1D for single text, 2D for list)
        """
        provider = self._load_provider()
        return provider.generate(text)

    def generate_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.

        Args:
            text: Text string

        Returns:
            1D numpy array of embedding
        """
        return self.generate(text)


class SimilarityCalculator:
    """Calculate semantic similarity between embeddings."""

    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        return float(dot_product / (norm1 * norm2))

    @staticmethod
    def euclidean_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Euclidean distance (lower is more similar)
        """
        return float(np.linalg.norm(embedding1 - embedding2))

    @staticmethod
    def similarity_score(
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        method: str = "cosine",
        threshold: float = 0.8,
    ) -> tuple[float, bool]:
        """
        Calculate similarity score and determine if embeddings are similar.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            method: Similarity method ('cosine' or 'euclidean')
            threshold: Threshold for considering embeddings similar

        Returns:
            Tuple of (similarity_score, is_similar)
        """
        if method == "cosine":
            score = SimilarityCalculator.cosine_similarity(embedding1, embedding2)
            is_similar = score >= threshold
        elif method == "euclidean":
            distance = SimilarityCalculator.euclidean_distance(embedding1, embedding2)
            # Convert distance to similarity (inverse, normalized)
            score = 1.0 / (1.0 + distance)
            is_similar = score >= threshold
        else:
            raise ValueError(f"Unknown similarity method: {method}")

        return score, is_similar

    @staticmethod
    def find_most_similar(
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        method: str = "cosine",
        top_k: int = 1,
    ) -> List[tuple[int, float]]:
        """
        Find the most similar embeddings to a query embedding.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            method: Similarity method ('cosine' or 'euclidean')
            top_k: Number of top results to return

        Returns:
            List of tuples (index, similarity_score) sorted by similarity
        """
        similarities = []
        for idx, candidate in enumerate(candidate_embeddings):
            if method == "cosine":
                score = SimilarityCalculator.cosine_similarity(query_embedding, candidate)
            else:
                distance = SimilarityCalculator.euclidean_distance(query_embedding, candidate)
                score = 1.0 / (1.0 + distance)

            similarities.append((idx, score))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
