
from abc import ABC, abstractmethod
from typing import List, Type, override

from data.db.sql import SQL
from models._base import BaseStruct
from utils.basic_types import Unassigned


class BaseProvider[T: BaseStruct](ABC):
    """
    Provides data from the database.
    """

    @abstractmethod
    def struct_type(self) -> Type[T]: ...
    """Override to provide the type of the struct this provider works with."""

    @override
    def __init__(self):
        super().__init__()
        self._list: List[T] = []
        for record in SQL(self.struct_type.db_table_name()).select(all=True):
            self._list.append(self.struct_type.from_record(record))

    def _is_equal(self, left: T, right: T) -> bool:
        for field in right.__dataclass_fields__.keys(): #type: ignore
            right_value = getattr(right, field)
            if right_value is Unassigned: continue
            if getattr(left, field) != right_value:
                return False
        return True

    def find(self, struct: T) -> T:
        """
        Find a struct in the list by comparing it with the provided struct.
        """
        return next((c for c in self._list if self._is_equal(c, struct)), None) #type: ignore

    def find_all(self, struct: T) -> List[T]:
        """
        Find all structs in the list that match the provided struct.
        """
        return [c for c in self._list if self._is_equal(c, struct)]