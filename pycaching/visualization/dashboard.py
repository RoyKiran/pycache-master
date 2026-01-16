"""Web dashboard using FastAPI for real-time cache monitoring."""

from typing import Dict, Optional

from pycaching.core.backend import Backend
from pycaching.visualization.metrics import MetricsCollector


class CacheDashboard:
    """Web dashboard for cache monitoring."""

    def __init__(
        self,
        backend: Optional[Backend] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        host: str = "0.0.0.0",
        port: int = 8000,
    ):
        """
        Initialize cache dashboard.

        Args:
            backend: Optional backend to monitor
            metrics_collector: Optional metrics collector
            host: Dashboard host
            port: Dashboard port
        """
        self.backend = backend
        self.metrics_collector = metrics_collector
        self.host = host
        self.port = port
        self._app = None

    def create_app(self):
        """Create FastAPI application."""
        try:
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse
        except ImportError:
            raise ImportError(
                "fastapi is required for CacheDashboard. Install with: pip install fastapi uvicorn"
            )

        app = FastAPI(title="Cache Dashboard")

        @app.get("/", response_class=HTMLResponse)
        async def root():
            """Dashboard home page."""
            return self._get_dashboard_html()

        @app.get("/api/stats")
        async def get_stats():
            """Get cache statistics."""
            stats = {}
            if self.metrics_collector:
                stats = self.metrics_collector.get_stats()
            if self.backend:
                stats["cache_size"] = self.backend.size()
            return stats

        @app.get("/api/metrics")
        async def get_metrics():
            """Get raw metrics."""
            if self.metrics_collector:
                return self.metrics_collector.export_dict()
            return {"metrics": []}

        return app

    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cache Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                .stat-card { background: #f0f0f0; padding: 15px; border-radius: 5px; }
                .stat-value { font-size: 24px; font-weight: bold; }
                .stat-label { color: #666; }
            </style>
        </head>
        <body>
            <h1>Cache Dashboard</h1>
            <div id="stats" class="stats"></div>
            <div id="charts"></div>
            <script>
                async function loadStats() {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    const statsDiv = document.getElementById('stats');
                    statsDiv.innerHTML = '';
                    for (const [key, value] of Object.entries(stats)) {
                        const card = document.createElement('div');
                        card.className = 'stat-card';
                        card.innerHTML = `
                            <div class="stat-label">${key}</div>
                            <div class="stat-value">${value}</div>
                        `;
                        statsDiv.appendChild(card);
                    }
                }
                setInterval(loadStats, 1000);
                loadStats();
            </script>
        </body>
        </html>
        """

    def run(self):
        """Run the dashboard server."""
        try:
            import uvicorn
        except ImportError:
            raise ImportError("uvicorn is required. Install with: pip install uvicorn")

        app = self.create_app()
        uvicorn.run(app, host=self.host, port=self.port)
