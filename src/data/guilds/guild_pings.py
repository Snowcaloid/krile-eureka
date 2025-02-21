from basic_types import GuildPingType
import bot
from typing import List

from data.db.sql import SQL, Record
from data.events.event_category import EventCategory

# TODO: technically, this could be united with guild_roles

class GuildPing:
    id: int
    type: GuildPingType
    event_type: str
    tag: int # user or role

    def load(self, id: int) -> None:
        record = SQL('pings').select(fields=['ping_type', 'schedule_type', 'tag'],
                                     where=f'id={id}')
        if record:
            self.id = id
            self.type = GuildPingType(record['ping_type'])
            self.event_type = record['schedule_type']
            self.tag = record['tag']

class GuildPings:
    _list: List[GuildPing] = []
    guild_id: int

    from data.events.event_templates import EventTemplates
    @EventTemplates.bind
    def event_templates(self) -> EventTemplates: ...

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self._list.clear()
        for record in SQL('pings').select(fields=['id'],
                                          where=f'guild_id={guild_id}',
                                          all=True):
            ping = GuildPing()
            ping.load(record['id'])
            self._list.append(ping)

    def get(self, ping_type: GuildPingType, event_type: str) -> List[GuildPing]:
        result = []
        for ping in self._list:
            if ping.type == ping_type and ping.event_type == event_type:
                result.append(ping)
        return result

    def add_ping_category(self, ping_type: GuildPingType, event_category: EventCategory, tag: int):
        query = Record() # Prevent multiple connects and disconnects
        for event_template in self.event_templates.get_by_categories(self.guild_id, [event_category]):
            self.add_ping(ping_type, event_template.type(), tag)
        del query

    def add_ping(self, ping_type: GuildPingType, event_type: str, tag: int):
        SQL('pings').insert(Record(guild_id=self.guild_id, ping_type=ping_type.value, schedule_type=event_type, tag=tag))
        self.load(self.guild_id)

    def remove_ping_category(self, ping_type: GuildPingType, event_category: EventCategory, tag: int):
        query = Record() # Prevent multiple connects and disconnects
        for event_template in self.event_templates.get_by_categories(self.guild_id, [event_category]):
            self.remove_ping(ping_type, event_template.type(), tag)
        del query

    def remove_ping(self, ping_type: GuildPingType, event_type: str, tag: int):
        SQL('pings').delete(f'guild_id={self.guild_id} and ping_type={ping_type.value} and schedule_type=\'{event_type}\' and tag={tag}')
        self.load(self.guild_id)

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
