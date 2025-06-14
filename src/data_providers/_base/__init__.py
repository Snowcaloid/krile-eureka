
from abc import ABC, abstractmethod
from typing import List, override

from data.db.sql import SQL
from models._base import BaseStruct
from utils.basic_types import Unassigned


class BaseProvider[T: BaseStruct](ABC):
    """
    Provides data from the database.
    When creating new providers, inherit from this class,
    setting the T-Type and overriding:
    * `db_table_name`
    """
    _list: List[T]

    @override
    def init(self):
        super().init()
        self._list = []
        for record in SQL(self.db_table_name()).select(all=True):
            self._list.append(T.from_record(record))

    def _is_equal(self, left: T, right: T) -> bool:
        for field in right.__dataclass_fields__.keys():
            right_value = getattr(right, field)
            if right_value is Unassigned: continue
            if getattr(left, field) != right_value:
                return False
        return True

    def find(self, struct: T) -> T:
        """
        Find a struct in the list by comparing it with the provided struct.
        """
        return next((c for c in self._list if self.is_equal(c, struct)), None)

    def find_all(self, struct: T) -> List[T]:
        """
        Find all structs in the list that match the provided struct.
        """
        return [c for c in self._list if self.is_equal(c, struct)]

    @abstractmethod
    def db_table_name(self) -> str: ...
    """Override to return the name of the database table for this provider."""