"""Base visualization interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class VisualizationBase(ABC):
    """Base class for visualization implementations."""

    @abstractmethod
    def render(self, data: Dict[str, Any]) -> Any:
        """
        Render visualization from data.

        Args:
            data: Data dictionary

        Returns:
            Rendered visualization
        """
        pass

    @abstractmethod
    def export(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Export visualization to file.

        Args:
            data: Data dictionary
            output_path: Output file path
        """
        pass
