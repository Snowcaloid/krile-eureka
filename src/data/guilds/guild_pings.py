import bot
from enum import Enum
from typing import List

from data.events.event import Event, EventCategory

class GuildPingType(Enum):
    NONE = 0
    MAIN_PASSCODE = 1
    SUPPORT_PASSCODE = 2
    PL_POST = 3

class GuildPing:
    id: int
    type: GuildPingType
    event_type: str
    tag: int # user or role

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select ping_type, schedule_type, tag from pings where id={id}')
            if record:
                self.id = id
                self.type = GuildPingType(record[0][0])
                self.event_type = record[0][1]
                self.tag = record[0][2]
        finally:
            db.disconnect()

class GuildPings:
    _list: List[GuildPing] = []
    guild_id: int

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        db = bot.instance.data.db
        db.connect()
        try:
            self._list.clear()
            records = db.query(f'select id from pings where guild_id={guild_id}')
            for record in records:
                ping = GuildPing()
                ping.load(record[0])
                self._list.append(ping)
        finally:
            db.disconnect()

    def get(self, ping_type: GuildPingType, event_type: str) -> List[GuildPing]:
        result = []
        for ping in self._list:
            if ping.type == ping_type and ping.event_type == event_type:
                result.append(ping)
        return result

    def add_ping_category(self, ping_type: GuildPingType, category: EventCategory, tag: int):
        db = bot.instance.data.db
        db.connect()
        try:
            for event_base in Event.all_events_for_category(category):
                self.add_ping(ping_type, event_base.type(), tag)
        finally:
            db.disconnect()

    def add_ping(self, ping_type: GuildPingType, event_type: str, tag: int):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'insert into pings (guild_id, ping_type, schedule_type, tag) values ({str(self.guild_id)}, {str(ping_type.value)}, \'{event_type}\', {str(tag)})')
            self.load()
        finally:
            db.disconnect()

    def remove_ping_category(self, ping_type: GuildPingType, category: EventCategory, tag: int):
        db = bot.instance.data.db
        db.connect()
        try:
            for event_base in category.all_events_for_category():
                self.remove_ping(ping_type, event_base.type(), tag)
        finally:
            db.disconnect()

    def remove_ping(self, ping_type: GuildPingType, event_type: str, tag: int):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from pings where guild_id={str(self.guild_id)} and ping_type={str(ping_type.value)} and schedule_type=\'{event_type}\' and tag={str(tag)}')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    async def get_mention_string(self, ping_type: GuildPingType, event_type: str) -> str:
        result = ''
        guild = bot.instance.get_guild(self.guild_id)
        if guild is None: return ''
        await guild.fetch_roles()
        for ping in self.get(ping_type, event_type):
            role = guild.get_role(ping.tag)
            if role:
                result += f'{role.mention} '
        return result.strip()
