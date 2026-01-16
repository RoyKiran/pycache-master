"""LLM caching examples."""

from pycaching.llm import SemanticCache, PromptCache, LLMCacheInterface
from pycaching.llm.embedding import EmbeddingGenerator


def example_semantic_cache():
    """Semantic similarity caching."""
    # Option 1: Use default model
    cache = SemanticCache(similarity_threshold=0.8)
    
    # Option 2: Pass model name directly
    cache = SemanticCache(
        model_name="sentence-transformers/all-mpnet-base-v2",  # Better model
        similarity_threshold=0.8,
    )
    
    # Option 3: Pass custom EmbeddingGenerator with specific device
    from pycaching.llm.embedding import EmbeddingGenerator
    embedding_gen = EmbeddingGenerator(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device="cuda",  # Use GPU if available
    )
    cache = SemanticCache(
        embedding_generator=embedding_gen,
        similarity_threshold=0.8,
    )

    # Cache a prompt-response pair
    cache.set("What is Python?", "Python is a high-level programming language...")

    # Get similar prompts
    response = cache.get("Tell me about Python")
    if response:
        print(f"Cached response: {response}")


def example_prompt_cache():
    """Prompt caching with token tracking."""
    cache = PromptCache()

    # Cache prompts
    cache.set("What is AI?", "AI is artificial intelligence...")

    # Get from cache
    response = cache.get("What is AI?")
    if response:
        print(f"Cached: {response}")

    # Get token stats
    stats = cache.get_token_stats()
    print(f"Token stats: {stats}")


def example_llm_interface():
    """LLM cache interface example."""
    # This requires an actual LLM provider
    # from pycaching.llm.model_interface import OpenAIProvider, LLMCacheInterface
    #
    # provider = OpenAIProvider(api_key="your-key")
    # 
    # # With semantic cache and custom embedding model
    # cache_interface = LLMCacheInterface(
    #     provider,
    #     use_semantic_cache=True,
    #     embedding_model_name="sentence-transformers/all-mpnet-base-v2",
    #     embedding_device="cuda",  # Use GPU if available
    #     similarity_threshold=0.85,
    # )
    #
    # response = await cache_interface.generate("What is Python?")
    # print(response)
    pass


def example_providers():
    """Example using different embedding providers with semantic cache."""
    # On-Premise Providers (no API keys needed)
    
    # HuggingFace (on-premise, local)
    cache_hf = SemanticCache(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold=0.8,
    )
    
    # Ollama (on-premise, local server)
    cache_ollama = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="ollama",
            model_name="nomic-embed-text",
            api_base="http://localhost:11434",
        ),
        similarity_threshold=0.8,
    )
    
    # Cloud Providers (require API keys)
    
    # OpenAI API
    cache_openai = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="openai",
            model_name="text-embedding-ada-002",
            api_key="your-openai-key",  # or set OPENAI_API_KEY env var
        ),
        similarity_threshold=0.8,
    )
    
    # Azure OpenAI
    cache_azure = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="azure",
            model_name="text-embedding-ada-002",
            api_key="your-azure-key",
            api_base="https://your-resource.openai.azure.com/",
        ),
        similarity_threshold=0.8,
    )
    
    # AWS Bedrock
    cache_aws = SemanticCache(
        embedding_generator=EmbeddingGenerator(
            provider="aws",
            model_name="amazon.titan-embed-text-v1",
            region="us-east-1",
        ),
        similarity_threshold=0.8,
    )
    
    # Use any cache
    cache_hf.set("What is Python?", "Python is a programming language...")
    response = cache_hf.get("Tell me about Python")
    if response:
        print(f"Cached response: {response}")


if __name__ == "__main__":
    example_semantic_cache()
    example_prompt_cache()
