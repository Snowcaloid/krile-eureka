from __future__ import annotations
from abc import ABC, abstractmethod

from data.db.sql import Record


class BaseStruct(ABC):
    """Override the class to define the actual data class.
    When creating a new struct, inherit from this class
    and implement the following methods:
    * `to_record()`
    * `from_record()`
    * `intersect()`
    * `__eq__()`
    * `__repr__()`
    * `changes_since()`
    * `marshal()`"""

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @abstractmethod
    def to_record(self) -> Record: ...
    """Override to create a database record from the struct."""

    @classmethod
    def from_record(cls, record: Record) -> BaseStruct: ...
    """Override to create an instance from a database record."""

    @abstractmethod
    def intersect(self, other: BaseStruct) -> BaseStruct: ...
    """Should yield a new struct that contains only the fields
    that are not None in both structs."""

    @abstractmethod
    def __eq__(self, other: BaseStruct) -> bool: ...
    """Override to compare two structs based on their fields."""

    @abstractmethod
    def __repr__(self) -> str: ...
    """Override to provide a string representation of the struct."""

    @abstractmethod
    def changes_since(self, other: BaseStruct) -> str: ...
    """Override to provide a string representation of the changes
    between this struct and another one."""

    @abstractmethod
    def marshal(self) -> dict: ...
    """Override to provide an object representation of the struct."""