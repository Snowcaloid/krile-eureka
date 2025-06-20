from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import fields
from datetime import datetime
from enum import Enum
from typing import Any, Self

from data.db.sql import Record
from utils.basic_types import Unassigned
from utils.functions import is_null_or_unassigned


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

    def _to_constructor_dict(self):
        return {
            field.name: getattr(self, field.name)
            for field in fields(self) #type: ignore
            if getattr(self, field.name) is not Unassigned
        }

    @classmethod
    def db_table_name(cls) -> str: raise NotImplementedError(
        "Override this method to provide the database table name for the struct."
    )

    @abstractmethod
    def type_name(self) -> str: ...

    @classmethod
    def from_record(cls, record: Record) -> Self:
        self = cls(**record)
        self.fixup_types()
        return self

    @abstractmethod
    def fixup_types(self) -> None: ...
    """Override to fix types that aren't compatible with the database."""

    @abstractmethod
    def identity(self) -> Self: ...

    def to_record(self) -> Record:
        return Record(**self._to_constructor_dict())

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

    def marshal_value(self, value: Any) -> Any:
        """Override to provide a custom marshaling for a value."""
        if is_null_or_unassigned(value):
            return None
        if isinstance(value, Enum):
            return value.name
        if isinstance(value, int) and value > 1000000000: # weak ass javascript
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value