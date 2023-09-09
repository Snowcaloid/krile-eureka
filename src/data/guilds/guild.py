from typing import List
import bot
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_missed_runs import GuildMissedRuns
from data.guilds.guild_pings import GuildPings
from data.guilds.guild_schedule import GuildSchedule


class Guild:
    id: int
    schedule: GuildSchedule
    channels: GuildChannels
    pings: GuildPings
    missed_runs: GuildMissedRuns

    def __init__(self):
        self.schedule = GuildSchedule()
        self.channels = GuildChannels()
        self.pings = GuildPings()
        self.missed_runs = GuildMissedRuns()

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.id = guild_id
            self.schedule.load(guild_id)
            self.channels.load(guild_id)
            self.pings.load(guild_id)
            self.missed_runs.load(guild_id)
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