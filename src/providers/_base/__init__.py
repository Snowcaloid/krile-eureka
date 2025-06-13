
from abc import ABC, abstractmethod
from typing import List, override

from centralized_data import Bindable, GlobalCollection

from data.db.sql import SQL
from models._base import BaseStruct
from utils.basic_types import GuildID


class BaseProvider[T: BaseStruct](Bindable, ABC):
    """
    Provides data from the database for a specific guild.
    When creating new providers, inherit from this class,
    setting the T-Type and overriding:
    * `db_table_name`
    """
    _list: List[T]

    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    @override
    def init(self):
        super().init()
        self._list = []
        self.load()

    def find(self, struct: T) -> T:
        """
        Find a struct in the list by comparing it with the provided struct.
        The comparison is done using the `__eq__` method of the struct.
        """
        return next((c for c in self._list if c == struct), None)

    def load(self) -> None:
        """
        Reload all data from the database for the current guild.
        This method should be called every time the data is changed.
        """
        self._list.clear()
        if self.key is None: return
        for record in SQL(self.db_table_name()).select(all=True):
            self._list.append(T.from_record(record))

    @abstractmethod
    def db_table_name(self) -> str: ...
    """Override to return the name of the database table for this provider."""

class BaseGuildProvider[T: BaseStruct](GlobalCollection[GuildID], ABC):
    """
    Provides data from the database for a specific guild.
    When creating new providers, inherit from this class,
    setting the T-Type and overriding:
    * `db_table_name`
    """
    _list: List[T]

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def find(self, struct: T) -> T:
        """
        Find a struct in the list by comparing it with the provided struct.
        The comparison is done using the `__eq__` method of the struct.
        """
        return next((c for c in self._list if c == struct), None)

    def load(self) -> None:
        """
        Reload all data from the database for the current guild.
        This method should be called every time the data is changed.
        """
        self._list.clear()
        if self.key is None: return
        for record in SQL(self.db_table_name()).select(where=f'guild_id={self.key}',
                                                       all=True):
            self._list.append(T.from_record(record))

    @abstractmethod
    def db_table_name(self) -> str: ...
    """Override to return the name of the database table for this provider."""

