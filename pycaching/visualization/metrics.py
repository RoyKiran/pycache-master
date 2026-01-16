"""Metrics collection system for cache performance tracking."""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
from threading import Lock

from pycaching.core.types import CacheKey


class CacheMetrics:
    """Metrics for a single cache operation."""

    def __init__(
        self,
        operation: str,
        key: Optional[CacheKey] = None,
        hit: bool = False,
        latency_ms: float = 0.0,
        timestamp: Optional[datetime] = None,
    ):
        self.operation = operation  # 'get', 'set', 'delete', etc.
        self.key = key
        self.hit = hit
        self.latency_ms = latency_ms
        self.timestamp = timestamp or datetime.now()


class MetricsCollector:
    """Collect and aggregate cache performance metrics."""

    def __init__(self, enabled: bool = True):
        """
        Initialize metrics collector.

        Args:
            enabled: Whether to collect metrics
        """
        self.enabled = enabled
        self._metrics: List[CacheMetrics] = []
        self._lock = Lock()
        self._operation_counts: Dict[str, int] = defaultdict(int)
        self._hit_counts: Dict[str, int] = defaultdict(int)
        self._miss_counts: Dict[str, int] = defaultdict(int)
        self._latency_sum: Dict[str, float] = defaultdict(float)
        self._start_time = datetime.now()

    def record(
        self,
        operation: str,
        key: Optional[CacheKey] = None,
        hit: bool = False,
        latency_ms: float = 0.0,
    ) -> None:
        """
        Record a cache operation metric.

        Args:
            operation: Operation type ('get', 'set', 'delete', etc.)
            key: Optional cache key
            hit: Whether it was a cache hit
            latency_ms: Operation latency in milliseconds
        """
        if not self.enabled:
            return

        metric = CacheMetrics(operation, key, hit, latency_ms)
        with self._lock:
            self._metrics.append(metric)
            self._operation_counts[operation] += 1
            if operation == "get":
                if hit:
                    self._hit_counts[operation] += 1
                else:
                    self._miss_counts[operation] += 1
            self._latency_sum[operation] += latency_ms

    def get_stats(self) -> Dict[str, any]:
        """
        Get aggregated statistics.

        Returns:
            Dictionary of statistics
        """
        with self._lock:
            total_operations = sum(self._operation_counts.values())
            total_gets = self._operation_counts.get("get", 0)
            total_hits = sum(self._hit_counts.values())
            total_misses = sum(self._miss_counts.values())

            hit_rate = (
                total_hits / total_gets if total_gets > 0 else 0.0
            )

            avg_latencies = {}
            for operation, count in self._operation_counts.items():
                if count > 0:
                    avg_latencies[operation] = self._latency_sum[operation] / count

            uptime_seconds = (datetime.now() - self._start_time).total_seconds()

            return {
                "total_operations": total_operations,
                "total_gets": total_gets,
                "total_hits": total_hits,
                "total_misses": total_misses,
                "hit_rate": hit_rate,
                "miss_rate": 1.0 - hit_rate if total_gets > 0 else 0.0,
                "operation_counts": dict(self._operation_counts),
                "average_latencies_ms": avg_latencies,
                "uptime_seconds": uptime_seconds,
                "operations_per_second": (
                    total_operations / uptime_seconds if uptime_seconds > 0 else 0.0
                ),
            }

    def get_metrics(self, limit: Optional[int] = None) -> List[CacheMetrics]:
        """
        Get raw metrics.

        Args:
            limit: Optional limit on number of metrics to return

        Returns:
            List of CacheMetrics
        """
        with self._lock:
            if limit is None:
                return self._metrics.copy()
            return self._metrics[-limit:]

    def clear(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._metrics.clear()
            self._operation_counts.clear()
            self._hit_counts.clear()
            self._miss_counts.clear()
            self._latency_sum.clear()
            self._start_time = datetime.now()

    def export_dict(self) -> Dict[str, any]:
        """Export metrics as dictionary."""
        stats = self.get_stats()
        metrics = [
            {
                "operation": m.operation,
                "key": str(m.key) if m.key else None,
                "hit": m.hit,
                "latency_ms": m.latency_ms,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in self._metrics
        ]
        return {
            "stats": stats,
            "metrics": metrics,
        }
