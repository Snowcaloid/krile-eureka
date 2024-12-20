from typing import List
from data.db.sql import SQL, Record
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_messages import GuildMessages
from data.guilds.guild_pings import GuildPings
from data.guilds.guild_roles import GuildRoles
from data.guilds.guild_schedule import GuildSchedule
from data.guilds.guild_signup_templates import GuildSignupTemplates


class Guild:
    id: int
    _role_developer: int
    _role_admin: int
    schedule: GuildSchedule
    channels: GuildChannels
    pings: GuildPings
    roles: GuildRoles
    messages: GuildMessages
    signup_templates: GuildSignupTemplates

    def __init__(self):
        self.schedule = GuildSchedule()
        self.channels = GuildChannels()
        self.pings = GuildPings()
        self.roles = GuildRoles()
        self.messages = GuildMessages()
        self.signup_templates = GuildSignupTemplates()

    def load(self, guild_id: int, soft_load: bool = False) -> None:
        query = Record() # Prevent multiple connects and disconnects
        self.id = guild_id
        record = SQL('guilds').select(fields=['role_developer', 'role_admin'],
                                      where=f'guild_id={self.id}')
        if record:
            self._role_developer = record['role_developer']
            self._role_admin = record['role_admin']
        if soft_load: return
        self.schedule.load(guild_id)
        self.channels.load(guild_id)
        self.pings.load(guild_id)
        self.roles.load(guild_id)
        self.messages.load(guild_id)
        self.signup_templates.load(guild_id)
        del query

    @property
    def role_developer(self) -> int: return self._role_developer

    @property
    def role_admin(self) -> int: return self._role_admin

    @role_developer.setter
    def role_developer(self, value: int) -> None:
        if value == self._role_developer: return
        SQL('guilds').update(Record(role_developer=value), f'guild_id={self.id}')
        self.load(self.id, True)

    @role_admin.setter
    def role_admin(self, value: int) -> None:
        if value == self._role_admin: return
        SQL('guilds').update(Record(role_admin=value), f'guild_id={self.id}')
        self.load(self.id, True)


class Guilds:
    _list: List[Guild] = []

    def load(self) -> None:
        self._list.clear()
        for record in SQL('guilds').select(fields=['guild_id'],
                                           all=True):
            guild = Guild()
            guild.load(record['guild_id'])
            self._list.append(guild)

    def get(self, guild_id: int) -> Guild:
        if not guild_id: return None
        for guild in self._list:
            if guild.id == guild_id:
                return guild
        SQL('guilds').insert(Record(guild_id=guild_id))
        self.load()
        return self.get(guild_id)

    @property
    def all(self) -> List[Guild]:
        return self._list