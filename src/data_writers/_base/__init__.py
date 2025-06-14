from __future__ import annotations
from abc import ABC, abstractmethod
from models.context import ExecutionContext


class BaseWriter[T](ABC):
    """Writes data to datbase."""

    @abstractmethod
    def sync(self, struct: T, context: ExecutionContext) -> None: ...
    """Override to sync a struct with the database."""

    @abstractmethod
    def remove(self, struct: T, context: ExecutionContext) -> None: ...
    """Override to remove a struct from the database."""