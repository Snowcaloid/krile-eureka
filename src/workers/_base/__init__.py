
from abc import ABC, abstractmethod
from centralized_data import Bindable

from models.context import ExecutionContext


class BaseWorker(Bindable, ABC):
    """Base class for workers that perform background tasks."""

    @abstractmethod
    def execute(self, context: ExecutionContext) -> None: ...
    """Override to implement the worker's main execution logic."""
