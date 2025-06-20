
from abc import ABC, abstractmethod
from typing import List, Optional, Type, override

from data.db.sql import ReadOnlyConnection, Record
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

    def _is_equal(self, left: T, right: T) -> bool:
        for field in right.__dataclass_fields__.keys(): #type: ignore
            right_value = getattr(right, field)
            if right_value is Unassigned: continue
            if getattr(left, field) != right_value:
                return False
        return True

    def _load(self, struct: Optional[T]) -> None:
        """
        Load the struct from the database and add it to the list.
        """
        with ReadOnlyConnection() as connection:
            self._list.clear()
            if struct is None:
                for record in connection.sql(self.struct_type.db_table_name()).select(all=True):
                    self._list.append(self.struct_type.from_record(record))
            else:
                for record in connection.sql(self.struct_type.db_table_name()).select(filter=struct.to_record(), all=True):
                    self._list.append(self.struct_type.from_record(record))

    def find(self, struct: T) -> T:
        """
        Find a struct in the list by comparing it with the provided struct.
        """
        return next((self.find_all(struct)), None) #type: ignore

    def find_all(self, struct: Optional[T] = None) -> List[T]:
        """
        Find all structs in the list that match the provided struct.
        """
        self._load(struct)
        return self._list

    def find_cached(self, struct: T) -> Optional[T]:
        """
        Find a struct in the list by comparing it with the provided struct.
        Returns None if not found.
        """
        return next((item for item in self._list if self._is_equal(item, struct)), None)

    @property
    def cache(self) -> List[T]:
        """
        Returns the cached list of structs.
        """
        return self._list

    def filter(self) -> Optional[Record]:
        return None