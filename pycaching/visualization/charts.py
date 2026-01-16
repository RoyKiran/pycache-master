"""Chart generation for cache visualization."""

from typing import Dict, List, Optional
from pathlib import Path

from pycaching.visualization.metrics import MetricsCollector


class ChartGenerator:
    """Generate charts for cache visualization."""

    def __init__(self, backend: str = "matplotlib"):
        """
        Initialize chart generator.

        Args:
            backend: Charting backend ('matplotlib' or 'plotly')
        """
        self.backend = backend.lower()

    def plot_hit_rate(
        self,
        metrics_collector: MetricsCollector,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot cache hit rate over time.

        Args:
            metrics_collector: MetricsCollector instance
            output_path: Optional output file path
        """
        stats = metrics_collector.get_stats()
        hit_rate = stats.get("hit_rate", 0.0)
        miss_rate = stats.get("miss_rate", 0.0)

        if self.backend == "matplotlib":
            try:
                import matplotlib.pyplot as plt
            except ImportError:
                raise ImportError("matplotlib is required. Install with: pip install matplotlib")

            fig, ax = plt.subplots()
            ax.bar(["Hit Rate", "Miss Rate"], [hit_rate, miss_rate])
            ax.set_ylabel("Rate")
            ax.set_title("Cache Hit/Miss Rate")
            ax.set_ylim(0, 1)

            if output_path:
                plt.savefig(output_path)
            else:
                plt.show()
        elif self.backend == "plotly":
            try:
                import plotly.graph_objects as go
            except ImportError:
                raise ImportError("plotly is required. Install with: pip install plotly")

            fig = go.Figure(data=[
                go.Bar(x=["Hit Rate", "Miss Rate"], y=[hit_rate, miss_rate])
            ])
            fig.update_layout(
                title="Cache Hit/Miss Rate",
                yaxis_title="Rate",
                yaxis_range=[0, 1],
            )
            if output_path:
                fig.write_html(output_path)
            else:
                fig.show()

    def plot_latency(
        self,
        metrics_collector: MetricsCollector,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot operation latencies.

        Args:
            metrics_collector: MetricsCollector instance
            output_path: Optional output file path
        """
        stats = metrics_collector.get_stats()
        latencies = stats.get("average_latencies_ms", {})

        if not latencies:
            return

        operations = list(latencies.keys())
        values = list(latencies.values())

        if self.backend == "matplotlib":
            try:
                import matplotlib.pyplot as plt
            except ImportError:
                raise ImportError("matplotlib is required. Install with: pip install matplotlib")

            fig, ax = plt.subplots()
            ax.bar(operations, values)
            ax.set_ylabel("Latency (ms)")
            ax.set_xlabel("Operation")
            ax.set_title("Average Operation Latency")

            if output_path:
                plt.savefig(output_path)
            else:
                plt.show()
        elif self.backend == "plotly":
            try:
                import plotly.graph_objects as go
            except ImportError:
                raise ImportError("plotly is required. Install with: pip install plotly")

            fig = go.Figure(data=[
                go.Bar(x=operations, y=values)
            ])
            fig.update_layout(
                title="Average Operation Latency",
                xaxis_title="Operation",
                yaxis_title="Latency (ms)",
            )
            if output_path:
                fig.write_html(output_path)
            else:
                fig.show()

    def plot_operations_over_time(
        self,
        metrics_collector: MetricsCollector,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Plot operations over time.

        Args:
            metrics_collector: MetricsCollector instance
            output_path: Optional output file path
        """
        metrics = metrics_collector.get_metrics()
        if not metrics:
            return

        # Group by time window
        from collections import defaultdict
        time_buckets = defaultdict(int)
        for metric in metrics:
            # Simple bucketing by minute
            bucket = metric.timestamp.strftime("%Y-%m-%d %H:%M")
            time_buckets[bucket] += 1

        times = sorted(time_buckets.keys())
        counts = [time_buckets[t] for t in times]

        if self.backend == "matplotlib":
            try:
                import matplotlib.pyplot as plt
            except ImportError:
                raise ImportError("matplotlib is required. Install with: pip install matplotlib")

            fig, ax = plt.subplots()
            ax.plot(times, counts)
            ax.set_ylabel("Operations")
            ax.set_xlabel("Time")
            ax.set_title("Operations Over Time")
            ax.tick_params(axis="x", rotation=45)

            if output_path:
                plt.savefig(output_path)
            else:
                plt.show()
        elif self.backend == "plotly":
            try:
                import plotly.graph_objects as go
            except ImportError:
                raise ImportError("plotly is required. Install with: pip install plotly")

            fig = go.Figure(data=[
                go.Scatter(x=times, y=counts, mode="lines+markers")
            ])
            fig.update_layout(
                title="Operations Over Time",
                xaxis_title="Time",
                yaxis_title="Operations",
            )
            if output_path:
                fig.write_html(output_path)
            else:
                fig.show()
