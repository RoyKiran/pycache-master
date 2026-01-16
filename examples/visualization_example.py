"""Visualization examples for cache monitoring."""

import time
from pycaching import create_cache
from pycaching.visualization.metrics import MetricsCollector
from pycaching.visualization.charts import ChartGenerator
from pycaching.visualization.json_exporter import JSONExporter
from pycaching.visualization.dashboard import CacheDashboard


def example_metrics_collection():
    """Example of collecting cache metrics."""
    # Create cache with metrics enabled
    cache = create_cache(backend="memory", strategy="cache_aside")
    
    # Create metrics collector
    metrics = MetricsCollector(enabled=True)
    
    # Simulate cache operations with metrics tracking
    for i in range(10):
        start_time = time.time()
        
        # Simulate cache operations
        if i % 3 == 0:
            # Cache miss
            value = cache.get(f"key_{i}")
            if value is None:
                cache.set(f"key_{i}", f"value_{i}")
                metrics.record("get", key=f"key_{i}", hit=False, latency_ms=(time.time() - start_time) * 1000)
        else:
            # Cache hit
            value = cache.get(f"key_{i}")
            metrics.record("get", key=f"key_{i}", hit=True, latency_ms=(time.time() - start_time) * 1000)
        
        # Record set operations
        start_time = time.time()
        cache.set(f"key_{i}", f"value_{i}")
        metrics.record("set", key=f"key_{i}", hit=False, latency_ms=(time.time() - start_time) * 1000)
    
    # Get statistics
    stats = metrics.get_stats()
    print("Cache Statistics:")
    print(f"  Total Operations: {stats['total_operations']}")
    print(f"  Hit Rate: {stats['hit_rate']:.2%}")
    print(f"  Miss Rate: {stats['miss_rate']:.2%}")
    print(f"  Average Latency: {stats['average_latencies_ms']}")
    
    return metrics


def example_charts():
    """Example of generating cache visualization charts."""
    # Collect some metrics first
    metrics = example_metrics_collection()
    
    # Create chart generator
    chart_gen = ChartGenerator(backend="matplotlib")
    
    # Generate hit rate chart
    print("\nGenerating hit rate chart...")
    chart_gen.plot_hit_rate(metrics, output_path="cache_hit_rate.png")
    print("  Saved to cache_hit_rate.png")
    
    # Generate latency chart
    print("\nGenerating latency chart...")
    chart_gen.plot_latency(metrics, output_path="cache_latency.png")
    print("  Saved to cache_latency.png")
    
    # Generate operations over time chart
    print("\nGenerating operations over time chart...")
    chart_gen.plot_operations_over_time(metrics, output_path="cache_operations.png")
    print("  Saved to cache_operations.png")
    
    # Using Plotly for interactive charts
    print("\nGenerating interactive Plotly charts...")
    plotly_gen = ChartGenerator(backend="plotly")
    plotly_gen.plot_hit_rate(metrics, output_path="cache_hit_rate.html")
    print("  Saved to cache_hit_rate.html")


def example_export():
    """Example of exporting cache data and metrics."""
    # Collect metrics
    metrics = example_metrics_collection()
    
    # Export metrics to JSON
    print("\nExporting metrics to JSON...")
    JSONExporter.export_metrics(metrics, "cache_metrics.json", format="json")
    print("  Saved to cache_metrics.json")
    
    # Export metrics to CSV
    print("\nExporting metrics to CSV...")
    JSONExporter.export_metrics(metrics, "cache_metrics.csv", format="csv")
    print("  Saved to cache_metrics.csv")
    
    # Export cache data
    cache = create_cache(backend="memory", strategy="cache_aside")
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    print("\nExporting cache data to JSON...")
    JSONExporter.export_cache_data(cache.backend, "cache_data.json", format="json")
    print("  Saved to cache_data.json")


def example_dashboard():
    """Example of running the cache dashboard."""
    cache = create_cache(backend="memory", strategy="cache_aside")
    metrics = MetricsCollector()
    
    # Create dashboard
    dashboard = CacheDashboard(
        backend=cache.backend,
        metrics_collector=metrics,
        host="0.0.0.0",
        port=8000,
    )
    
    print("\nStarting cache dashboard...")
    print("  Access at: http://localhost:8000")
    print("  API stats at: http://localhost:8000/api/stats")
    print("  API metrics at: http://localhost:8000/api/metrics")
    print("\nPress Ctrl+C to stop the dashboard")
    
    # Uncomment to run dashboard
    # dashboard.run()


if __name__ == "__main__":
    print("=== Cache Visualization Examples ===\n")
    
    # Example 1: Metrics Collection
    print("1. Metrics Collection Example")
    print("-" * 40)
    example_metrics_collection()
    
    # Example 2: Charts
    print("\n\n2. Charts Example")
    print("-" * 40)
    try:
        example_charts()
    except ImportError as e:
        print(f"  Skipping charts (missing dependency): {e}")
    
    # Example 3: Export
    print("\n\n3. Export Example")
    print("-" * 40)
    example_export()
    
    # Example 4: Dashboard
    print("\n\n4. Dashboard Example")
    print("-" * 40)
    print("  Dashboard code is ready. Uncomment dashboard.run() to start.")
    # example_dashboard()
