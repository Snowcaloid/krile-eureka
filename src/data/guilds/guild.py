from typing import List
import bot
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_messages import GuildMessages
from data.guilds.guild_pings import GuildPings
from data.guilds.guild_roles import GuildRoles
from data.guilds.guild_schedule import GuildSchedule


class Guild:
    id: int
    _role_developer: int
    _role_admin: int
    schedule: GuildSchedule
    channels: GuildChannels
    pings: GuildPings
    roles: GuildRoles
    messages: GuildMessages

    def __init__(self):
        self.schedule = GuildSchedule()
        self.channels = GuildChannels()
        self.pings = GuildPings()
        self.roles = GuildRoles()
        self.messages = GuildMessages()

    def load(self, guild_id: int, soft_load: bool = False) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.id = guild_id
            record = db.query(f'select role_developer, role_admin from guilds where guild_id={self.id}')
            if record:
                self._role_developer = record[0][0]
                self._role_admin = record[0][1]
            if soft_load: return
            self.schedule.load(guild_id)
            self.channels.load(guild_id)
            self.pings.load(guild_id)
            self.roles.load(guild_id)
            self.messages.load(guild_id)
        finally:
            db.disconnect()

    @property
    def role_developer(self) -> int: return self._role_developer

    @property
    def role_admin(self) -> int: return self._role_admin

    @role_developer.setter
    def role_developer(self, value: int) -> None:
        if value == self._role_developer: return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update guilds set role_developer={value} where guild_id={self.id}')
            self.load(self.id, True)
        finally:
            db.disconnect()

    @role_admin.setter
    def role_admin(self, value: int) -> None:
        if value == self._role_admin: return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update guilds set role_admin={value} where guild_id={self.id}')
            self.load(self.id, True)
        finally:
            db.disconnect()


class Guilds:
    _list: List[Guild] = []

    def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self._list.clear()
            records = db.query('select guild_id from guilds')
            for record in records:
                guild = Guild()
                guild.load(record[0])
                self._list.append(guild)
        finally:
            db.disconnect()

    def get(self, guild_id: int) -> Guild:
        if not guild_id: return None
        for guild in self._list:
            if guild.id == guild_id:
                return guild
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'insert into guilds (guild_id) values ({guild_id})')
            self.load()
            return self.get(guild_id)
        finally:
            db.disconnect()

    @property
    def all(self) -> List[Guild]:
        return self._list