"""JSON/CSV export functionality for cache data."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from pycaching.core.backend import Backend
from pycaching.core.types import CacheKey, CacheValue
from pycaching.visualization.metrics import MetricsCollector


class JSONExporter:
    """Export cache data and metrics to JSON/CSV."""

    @staticmethod
    def export_cache_data(
        backend: Backend,
        output_path: str,
        format: str = "json",
    ) -> None:
        """
        Export cache data to file.

        Args:
            backend: Backend to export from
            output_path: Output file path
            format: Export format ('json' or 'csv')
        """
        output_path = Path(output_path)
        data = []

        # Collect all cache entries
        for key in backend.keys():
            value = backend.get(key)
            data.append({
                "key": str(key),
                "value": str(value) if value is not None else None,
                "exists": backend.exists(key),
            })

        if format.lower() == "json":
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        elif format.lower() == "csv":
            with open(output_path, "w", newline="") as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def export_metrics(
        metrics_collector: MetricsCollector,
        output_path: str,
        format: str = "json",
    ) -> None:
        """
        Export metrics to file.

        Args:
            metrics_collector: MetricsCollector instance
            output_path: Output file path
            format: Export format ('json' or 'csv')
        """
        output_path = Path(output_path)
        data = metrics_collector.export_dict()

        if format.lower() == "json":
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        elif format.lower() == "csv":
            # Export metrics as CSV
            with open(output_path, "w", newline="") as f:
                if data["metrics"]:
                    writer = csv.DictWriter(f, fieldnames=data["metrics"][0].keys())
                    writer.writeheader()
                    writer.writerows(data["metrics"])
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def export_stats(
        stats: Dict[str, Any],
        output_path: str,
    ) -> None:
        """
        Export statistics to JSON file.

        Args:
            stats: Statistics dictionary
            output_path: Output file path
        """
        output_path = Path(output_path)
        with open(output_path, "w") as f:
            json.dump(stats, f, indent=2)
