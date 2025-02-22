from typing import List

from data.db.sql import SQL, Record
from basic_types import GuildRoleFunction

class GuildRole:
    id: int
    role_id: int
    event_category: str
    function: GuildRoleFunction

    def load(self, id: int) -> None:
        record = SQL('guild_roles').select(fields=['role_id', 'event_category', 'function'],
                                           where=f'id={id}')
        if record:
            self.id = id
            self.role_id = record['role_id']
            self.event_category = record['event_category']
            self.function = GuildRoleFunction(record['function'])

class GuildRoles:
    _list: List[GuildRole] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self._list.clear()
        for record in SQL('guild_roles').select(fields=['id'],
                                                where=f'guild_id={guild_id}',
                                                all=True):
            channel = GuildRole()
            channel.load(record['id'])
            self._list.append(channel)

    def get(self, function: GuildRoleFunction = GuildRoleFunction.NONE, event_category: str = '') -> List[GuildRole]:
        return [role for role in self._list if role.function == function and (not event_category or role.event_category == event_category)]

    def get_by_id(self, role_id: int) -> List[GuildRole]:
        return [role for role in self._list if role.role_id == role_id]

    def add(self, role_id: int, function: GuildRoleFunction, event_category: str = '') -> None:
        SQL('guild_roles').insert(Record(guild_id=self.guild_id, role_id=role_id, function=function.value, event_category=event_category))
        self.load(self.guild_id)

    def remove(self, role_id: int, function: GuildRoleFunction, event_category: str = '') -> None:
        event_category_part = f'and event_category=\'{event_category}\'' if event_category else ''
        SQL('guild_roles').delete(f'guild_id={self.guild_id} and role_id={role_id} and function={function.value} {event_category_part}')
        self.load(self.guild_id)