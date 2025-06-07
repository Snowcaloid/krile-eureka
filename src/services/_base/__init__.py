from __future__ import annotations
from abc import abstractmethod
from centralized_data import Bindable, GlobalCollection
from models.context import ExecutionContext
from utils.basic_types import GuildID


class BaseService[T](Bindable):
    """Writes data to datbase."""

    @abstractmethod
    def sync(self, struct: T, context: ExecutionContext) -> None: ...
    """Override to sync a struct with the database."""

    @abstractmethod
    def remove(self, struct: T, context: ExecutionContext) -> None: ...
    """Override to remove a struct from the database."""


class BaseGuildService[T](GlobalCollection[GuildID]):
    """Writes data to datbase for a specific guild."""

    @abstractmethod
    def sync(self, struct: T, context: ExecutionContext) -> None: ...
    """Override to sync a struct with the database."""

    @abstractmethod
    def remove(self, struct: T, context: ExecutionContext) -> None: ...
    """Override to remove a struct from the database."""