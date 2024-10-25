import bot
from typing import List

from data.guilds.guild_role_functions import GuildRoleFunction

class GuildRole:
    id: int
    role_id: int
    event_category: str
    function: GuildRoleFunction

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select role_id, event_category, function from guild_roles where id={id}')
            if record:
                self.id = id
                self.role_id = record[0][0]
                self.event_category = record[0][1]
                self.function = GuildRoleFunction(record[0][2])
        finally:
            db.disconnect()

class GuildRoles:
    _list: List[GuildRole] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self._list.clear()
            records = db.query(f'select id from guild_roles where guild_id={guild_id}')
            for record in records:
                channel = GuildRole()
                channel.load(record[0])
                self._list.append(channel)
        finally:
            db.disconnect()

    def get(self, function: GuildRoleFunction = GuildRoleFunction.NONE, event_category: str = '') -> List[GuildRole]:
        return [role for role in self._list if role.function == function and (not event_category or role.event_category == event_category)]

    def add(self, role_id: int, function: GuildRoleFunction, event_category: str = '') -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'insert into guild_roles (guild_id, function, event_category, role_id) values ({str(self.guild_id)}, {str(function.value)}, \'{event_category}\', {str(role_id)})')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def remove(self, role_id: int, function: GuildRoleFunction, event_category: str = '') -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            event_category_part = f'and event_category=\'{event_category}\'' if event_category else ''
            db.query(f'delete from guild_roles where guild_id={str(self.guild_id)} and function={str(function.value)} {event_category_part} and role_id={role_id}')
            self.load(self.guild_id)
        finally:
            db.disconnect()