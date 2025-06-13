from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import fields
from typing import Self

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

    def __init__(self):
        super().__init__()
        self.fixup_types()

    def _to_constructor_dict(self):
        return {field.name: getattr(self, field.name) for field in fields(self)} #type: ignore

    @classmethod
    def from_record(cls, record: Record) -> Self:
        return cls(**record)

    @abstractmethod
    def fixup_types(self) -> None: ...
    """Override to fix types that aren't compatible with the database."""

    def to_record(self) -> Record:
        return Record(self._to_constructor_dict())

    def intersect(self, other: Self) -> Self:
        result = self.__class__(**self._to_constructor_dict())
        for field in fields(other): #type: ignore
            value = getattr(other, field.name)
            if value is not Unassigned:
                setattr(result, field.name, value)
        return result

    @abstractmethod
    def __repr__(self) -> str: ...
    """Override to provide a string representation of the struct."""

    @abstractmethod
    def changes_since(self, other: BaseStruct) -> str: ...
    """Override to provide a string representation of the changes
    between this struct and another one."""

    @abstractmethod
    def marshal(self) -> dict: ...
    """Override to provide an dict representation of the struct."""