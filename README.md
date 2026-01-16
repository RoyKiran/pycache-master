# py-caching-master
Modular Python caching library for microservices, databases, and LLM workflows. Configurable strategies like cache-aside, write-through, TTL, Redis/ElastiCache, Memcached &amp; semantic LLM caching with inspection tools, backend abstraction, and backend metrics. Boost performance, reduce latency, and scale caching across apps.

## Features

- **Multiple Backends**: Memory, File, SQLite, Redis, Memcached, MongoDB, ElastiCache, Cloudflare KV
- **Caching Strategies**: Cache-aside, Write-through, Write-back, Read-through, Refresh-ahead
- **Eviction Policies**: LRU, LFU, FIFO
- **LLM Support**: Semantic similarity caching, prompt caching, token tracking
- **Embedding Providers**: HuggingFace, Ollama (on-premise), OpenAI, Azure, AWS Bedrock
- **Async Support**: Full async/await support with sync wrappers
- **Multiple APIs**: Decorator, context manager, class-based, functional
- **Visualization**: Metrics collection, charts, web dashboard
- **Type Safe**: Full type hints throughout

## Installation

```bash
pip install pycaching
```

### Optional Dependencies
```bash
# Redis support
pip install pycaching[redis]

# Memcached support
pip install pycaching[memcached]

# MongoDB support
pip install pycaching[mongodb]

# LLM features
pip install pycaching[llm]

# Visualization
pip install pycaching[visualization]

# All features
pip install pycaching[all]
```

## Quick Start

### Basic Usage
```python
from pycaching import create_cache

# Create a cache
cache = create_cache(backend="memory", strategy="cache_aside")

# Set and get values
cache.set("key1", "value1")
value = cache.get("key1")
print(value)  # "value1"
```

### Decorator API
```python
from pycaching.api.decorator import cache

@cache(ttl=3600)
def expensive_function(x):
    # Expensive computation
    return x * 2

result = expensive_function(5)  # Cached for 1 hour
```

### Context Manager API
```python
from pycaching.api.context import CacheContext

with CacheContext("my_key") as ctx:
    value = ctx.get_or_compute(lambda key: compute_expensive_value())
```

### Functional API
```python
from pycaching.api.functional import cache

cache.set("key1", "value1")
value = cache.get("key1")
```

### Redis Backend
```python
from pycaching import create_cache

cache = create_cache(
    backend="redis",
    host="localhost",
    port=6379,
)
```

### LLM Semantic Caching
```python
from pycaching.llm import SemanticCache
from pycaching.llm.embedding import EmbeddingGenerator

# On-Premise Providers (no API keys needed)

# Using HuggingFace (default, local)
semantic_cache = SemanticCache(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    similarity_threshold=0.8
)

# Using Ollama (local server)
semantic_cache = SemanticCache(
    embedding_generator=EmbeddingGenerator(
        provider="ollama",
        model_name="nomic-embed-text",  # or "all-minilm", "mxbai-embed-large"
        api_base="http://localhost:11434",  # your Ollama server
    ),
    similarity_threshold=0.8,
)

# Cloud Providers (require API keys)

# Using OpenAI API
semantic_cache = SemanticCache(
    embedding_generator=EmbeddingGenerator(
        provider="openai",
        model_name="text-embedding-ada-002",
        api_key="your-key",  # or set OPENAI_API_KEY env var
    ),
    similarity_threshold=0.8,
)

# Using Azure OpenAI
semantic_cache = SemanticCache(
    embedding_generator=EmbeddingGenerator(
        provider="azure",
        model_name="text-embedding-ada-002",
        api_key="your-key",
        api_base="https://your-resource.openai.azure.com/",
    ),
    similarity_threshold=0.8,
)

# Using AWS Bedrock
semantic_cache = SemanticCache(
    embedding_generator=EmbeddingGenerator(
        provider="aws",
        model_name="amazon.titan-embed-text-v1",
        region="us-east-1",
    ),
    similarity_threshold=0.8,
)

# Cache a prompt-response pair
semantic_cache.set("What is Python?", "Python is a programming language...")

# Get similar prompts
response = semantic_cache.get("Tell me about Python")
# Returns cached response if similarity > 0.8
```

### Visualization
```python
from pycaching.visualization import MetricsCollector, ChartGenerator, JSONExporter

# Collect metrics
metrics = MetricsCollector()
# ... perform cache operations and record metrics

# Generate charts
chart_gen = ChartGenerator(backend="matplotlib")
chart_gen.plot_hit_rate(metrics, output_path="hit_rate.png")
chart_gen.plot_latency(metrics, output_path="latency.png")

# Export metrics
JSONExporter.export_metrics(metrics, "metrics.json")
```

## Documentation

### Backends
- **Memory**: In-memory dictionary-based backend
- **File**: File-based persistent backend
- **SQLite**: SQLite database backend
- **Redis**: Redis backend with connection pooling
- **Memcached**: Memcached backend
- **MongoDB**: MongoDB backend
- **ElastiCache**: AWS ElastiCache (Redis-compatible)
- **Cloudflare KV**: Cloudflare KV backend

### Strategies
- **Cache-Aside**: Lazy loading pattern
- **Write-Through**: Write to cache and data store simultaneously
- **Write-Back**: Write to cache, async write to data store
- **Read-Through**: Automatic loading from data store on miss
- **Refresh-Ahead**: Proactive refresh before expiration

### Eviction Policies
- **LRU**: Least Recently Used
- **LFU**: Least Frequently Used
- **FIFO**: First In First Out

## Examples
See the `examples/` directory for more usage examples:

- `basic_usage.py` - Basic cache operations
- `llm_caching.py` - LLM caching with semantic similarity
- `embedding_providers.py` - Using different embedding providers (OpenAI, Azure, AWS, HuggingFace)
- `visualization_example.py` - Cache metrics and visualization

## License
MIT

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.
(All about caching)
