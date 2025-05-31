from typing import List

from centralized_data import GlobalCollection

from data.db.sql import SQL, Record
from utils.basic_types import GuildID, GuildChannelFunction

class GuildRole:
    id: int
    role_id: int
    event_category: str
    function: GuildChannelFunction

    def load(self, id: int) -> None:
        record = SQL('guild_roles').select(fields=['role_id', 'event_category', 'function'],
                                           where=f'id={id}')
        if record:
            self.id = id
            self.role_id = record['role_id']
            self.event_category = record['event_category']
            self.function = GuildChannelFunction(record['function'])

class GuildRoles(GlobalCollection[GuildID]):
    _list: List[GuildRole]

    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('guild_roles').select(fields=['id'],
                                                where=f'guild_id={self.key}',
                                                all=True):
            channel = GuildRole()
            channel.load(record['id'])
            self._list.append(channel)

    def get(self, function: GuildChannelFunction = GuildChannelFunction.NONE, event_category: str = '') -> List[GuildRole]:
        return [role for role in self._list if role.function == function and (not event_category or role.event_category == event_category)]

    def get_by_id(self, role_id: int) -> List[GuildRole]:
        return [role for role in self._list if role.role_id == role_id]

    def add(self, role_id: int, function: GuildChannelFunction, event_category: str = '') -> None:
        SQL('guild_roles').insert(Record(guild_id=self.key, role_id=role_id, function=function.value, event_category=event_category))
        self.load()

    def remove(self, role_id: int, function: GuildChannelFunction, event_category: str = '') -> None:
        event_category_part = f'and event_category=\'{event_category}\'' if event_category else ''
        SQL('guild_roles').delete(f'guild_id={self.key} and role_id={role_id} and function={function.value} {event_category_part}')
        self.load()