from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import fields

from data.db.sql import Record
from utils.basic_types import Unassigned


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

    def __init__(self):
        super().__init__()
        self.fixup_enums()

    def _to_constructor_dict(self):
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_record(cls, record: Record) -> BaseStruct:
        return cls(**record)

    @abstractmethod
    def fixup_enums(self) -> None: ...
    """Override to change enum fields into actual enums."""

    def to_record(self) -> Record:
        return Record(self._to_constructor_dict())

    def intersect(self, other: BaseStruct) -> BaseStruct:
        result = self.__class__(self._to_constructor_dict())
        for field in fields(other):
            value = getattr(other, field.name)
            if value is not Unassigned:
                setattr(result, field.name, value)
        return result

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