
from typing import Dict, List

from data.runtime_guild_data import RuntimeGuildData
from data.table.pings import PingType, PingsData
from data.table.schedule import ScheduleType
import bot


class PingsRuntimeData:
    _list: Dict[int, List[PingsData]]

    def __init__(self):
        self._list = {}


    def get_data(self, guild: int) -> List[PingsData]:
        if not guild in self._list:
            self._list[guild] = []

        return self._list[guild]


    def find_data(self, guild: int, ping_type: PingType, schedule_type: ScheduleType) -> PingsData:
        for data in self.get_data(guild):
            if data.ping_type == ping_type and data.schedule_type == schedule_type:
                return data
        data = PingsData(guild, ping_type, schedule_type, [])
        self.get_data(guild).append(data)
        return data


    def add_ping(self, guild: int, ping_type: PingType, schedule_type: ScheduleType, tag: int):
        if schedule_type == ScheduleType.BA_ALL:
            self.add_ping(guild, ping_type, ScheduleType.BA_NORMAL, tag)
            self.add_ping(guild, ping_type, ScheduleType.BA_RECLEAR, tag)
            self.add_ping(guild, ping_type, ScheduleType.BA_SPECIAL, tag)
            return

        if schedule_type == ScheduleType.DRS_ALL:
            self.add_ping(guild, ping_type, ScheduleType.DRS_NORMAL, tag)
            self.add_ping(guild, ping_type, ScheduleType.DRS_RECLEAR, tag)
            return

        db = bot.krile.data.db
        if not db.connected():
            db.connect()
            try:
                db.query(f'insert into pings (guild_id, ping_type, schedule_type, tag) values ({str(guild)}, {str(ping_type.value)}, \'{schedule_type.value}\', {str(tag)})')
            finally:
                db.disconnect()

        data: PingsData = self.find_data(guild, ping_type, schedule_type)
        data.tags.append(tag)


    def remove_ping(self, guild: int, ping_type: PingType, schedule_type: ScheduleType, tag: int):
        if schedule_type == ScheduleType.BA_ALL:
            self.remove_ping(guild, ping_type, ScheduleType.BA_NORMAL, tag)
            self.remove_ping(guild, ping_type, ScheduleType.BA_RECLEAR, tag)
            self.remove_ping(guild, ping_type, ScheduleType.BA_SPECIAL, tag)
            return

        if schedule_type == ScheduleType.DRS_ALL:
            self.remove_ping(guild, ping_type, ScheduleType.DRS_NORMAL, tag)
            self.remove_ping(guild, ping_type, ScheduleType.DRS_RECLEAR, tag)
            return

        db = bot.krile.data.db
        db.connect()
        try:
            db.query(f'delete from pings where guild_id={str(guild)} and ping_type={str(ping_type.value)} and schedule_type=\'{schedule_type.value}\' and tag={str(tag)}')
        finally:
            db.disconnect()

        data: PingsData = self.find_data(guild, ping_type, schedule_type)
        data.tags.remove(tag)


    def load(self, guild_data: RuntimeGuildData):
        db = bot.krile.data.db
        db.connect()
        try:
            for guild in guild_data._list:
                record = db.query(f'select ping_type, schedule_type, tag from pings where guild_id={guild.guild_id}')
                for row in record:
                    self.add_ping(guild.guild_id, PingType(row[0]), ScheduleType(row[1]), row[2])
        finally:
            db.disconnect()

    async def get_mention_string(self, guild_id: int, ping_type: PingType, schedule_type: ScheduleType) -> str:
        result = ''
        guild = bot.krile.get_guild(guild_id)
        if guild:
            await guild.fetch_roles()
            data = self.find_data(guild_id, ping_type, schedule_type)
            for id in data.tags:
                role = guild.get_role(id)
                if role:
                    result += f'{role.mention} '
        return result.strip()