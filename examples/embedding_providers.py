"""Examples of using different embedding providers."""

from pycaching.llm.embedding import EmbeddingGenerator
from pycaching.llm.semantic_cache import SemanticCache


def example_huggingface():
    """Example using HuggingFace sentence-transformers (on-premise/local)."""
    print("=== HuggingFace Embedding Provider (On-Premise) ===")
    
    # Default model - runs locally, no API needed
    generator = EmbeddingGenerator(
        provider="huggingface",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    )
    
    # Or specify a different model
    generator = EmbeddingGenerator(
        provider="huggingface",
        model_name="sentence-transformers/all-mpnet-base-v2",
        device="cpu",  # or "cuda" for GPU
    )
    
    embedding = generator.generate_single("Hello, world!")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding (first 5 values): {embedding[:5]}")


def example_ollama():
    """Example using Ollama (on-premise/local)."""
    print("\n=== Ollama Embedding Provider (On-Premise) ===")
    
    # Default - connects to local Ollama server
    generator = EmbeddingGenerator(
        provider="ollama",
        model_name="nomic-embed-text",  # or "all-minilm", "mxbai-embed-large", etc.
    )
    
    # Custom Ollama server URL
    generator = EmbeddingGenerator(
        provider="ollama",
        model_name="nomic-embed-text",
        api_base="http://localhost:11434",  # or your Ollama server URL
    )
    
    # Or use base_url in kwargs
    generator = EmbeddingGenerator(
        provider="ollama",
        model_name="all-minilm",
        base_url="http://localhost:11434",
    )
    
    embedding = generator.generate_single("Hello, world!")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding (first 5 values): {embedding[:5]}")


def example_openai():
    """Example using OpenAI embeddings API."""
    print("\n=== OpenAI Embedding Provider ===")
    
    # Using API key parameter
    generator = EmbeddingGenerator(
        provider="openai",
        model_name="text-embedding-ada-002",  # or text-embedding-3-small, text-embedding-3-large
        api_key="your-openai-api-key",
    )
    
    # Or using environment variable OPENAI_API_KEY
    generator = EmbeddingGenerator(
        provider="openai",
        model_name="text-embedding-3-small",
    )
    
    embedding = generator.generate_single("Hello, world!")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding (first 5 values): {embedding[:5]}")


def example_azure():
    """Example using Azure OpenAI embeddings."""
    print("\n=== Azure OpenAI Embedding Provider ===")
    
    generator = EmbeddingGenerator(
        provider="azure",
        model_name="text-embedding-ada-002",
        api_key="your-azure-api-key",
        api_base="https://your-resource.openai.azure.com/",
        api_version="2023-05-15",  # Passed via kwargs
    )
    
    # Or using environment variables
    # AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    generator = EmbeddingGenerator(
        provider="azure",
        model_name="text-embedding-ada-002",
    )
    
    embedding = generator.generate_single("Hello, world!")
    print(f"Embedding shape: {embedding.shape}")


def example_aws():
    """Example using AWS Bedrock embeddings."""
    print("\n=== AWS Bedrock Embedding Provider ===")
    
    generator = EmbeddingGenerator(
        provider="aws",
        model_name="amazon.titan-embed-text-v1",  # or amazon.titan-embed-text-v2
        region="us-east-1",
    )
    
    # AWS credentials are typically from ~/.aws/credentials or environment
    embedding = generator.generate_single("Hello, world!")
    print(f"Embedding shape: {embedding.shape}")


def example_custom():
    """Example using custom embedding provider."""
    print("\n=== Custom Embedding Provider ===")
    
    def my_custom_embedding(text):
        """Custom embedding function - must return numpy array."""
        import numpy as np
        # Example: simple hash-based embedding (not recommended for production)
        if isinstance(text, str):
            # Convert text to simple embedding
            embedding = np.array([hash(text) % 1000] * 384, dtype=np.float32)
            return embedding / np.linalg.norm(embedding)  # Normalize
        else:
            return np.array([my_custom_embedding(t) for t in text])
    
    generator = EmbeddingGenerator(
        provider="custom",
        custom_provider=my_custom_embedding,
    )
    
    embedding = generator.generate_single("Hello, world!")
    print(f"Embedding shape: {embedding.shape}")


def example_semantic_cache_with_providers():
    """Example using different providers with semantic cache."""
    print("\n=== Semantic Cache with Different Providers ===")
    
    # Option 1: HuggingFace (on-premise, no API key needed)
    cache_hf = SemanticCache(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold=0.8,
    )
    
    # Option 2: Ollama (on-premise, no API key needed)
    cache_ollama = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="ollama",
            model_name="nomic-embed-text",
            api_base="http://localhost:11434",
        ),
        similarity_threshold=0.8,
    )
    
    # Option 3: OpenAI (cloud, requires API key)
    cache_openai = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="openai",
            model_name="text-embedding-ada-002",
            api_key="your-key",  # or use env var
        ),
        similarity_threshold=0.8,
    )
    
    # Option 4: Azure (cloud, requires API key)
    cache_azure = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="azure",
            model_name="text-embedding-ada-002",
            api_key="your-key",
            api_base="https://your-resource.openai.azure.com/",
        ),
        similarity_threshold=0.8,
    )
    
    # Option 5: AWS (cloud, requires credentials)
    cache_aws = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="aws",
            model_name="amazon.titan-embed-text-v1",
            region="us-east-1",
        ),
        similarity_threshold=0.8,
    )
    
    # Use any of the caches
    cache_hf.set("What is Python?", "Python is a programming language...")
    response = cache_hf.get("Tell me about Python")
    print(f"Cached response: {response}")


if __name__ == "__main__":
    # Uncomment the examples you want to run
    
    # On-premise providers (no API keys needed)
    # example_huggingface()
    # example_ollama()
    
    # Cloud providers (require API keys)
    # example_openai()
    # example_azure()
    # example_aws()
    
    # Custom provider
    # example_custom()
    
    # Semantic cache with providers
    # example_semantic_cache_with_providers()
    
    print("\nNote: Uncomment the examples above.")
    print("On-premise providers (HuggingFace, Ollama) don't require API keys.")
    print("Cloud providers (OpenAI, Azure, AWS) require API keys.")
