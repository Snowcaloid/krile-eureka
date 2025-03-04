from centralized_data import GlobalCollection
from utils.basic_types import GuildID, GuildPingType
from typing import List, override

from data.db.sql import SQL, Record
from data.events.event_category import EventCategory
from data.events.event_templates import EventTemplates

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

class GuildPings(GlobalCollection[GuildID]):
    _list: List[GuildPing]

    from bot import DiscordClient
    @DiscordClient.bind
    def client(self) -> DiscordClient: ...

    @override
    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('pings').select(fields=['id'],
                                          where=f'guild_id={self.key}',
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
        for event_template in EventTemplates(self.key).get_by_categories([event_category]):
            self.add_ping(ping_type, event_template.type(), tag)
        del query

    def add_ping(self, ping_type: GuildPingType, event_type: str, tag: int):
        SQL('pings').insert(Record(guild_id=self.key, ping_type=ping_type.value, schedule_type=event_type, tag=tag))
        self.load()

    def remove_ping_category(self, ping_type: GuildPingType, event_category: EventCategory, tag: int):
        query = Record() # Prevent multiple connects and disconnects
        for event_template in EventTemplates(self.key).get_by_categories([event_category]):
            self.remove_ping(ping_type, event_template.type(), tag)
        del query

    def remove_ping(self, ping_type: GuildPingType, event_type: str, tag: int):
        SQL('pings').delete(f'guild_id={self.key} and ping_type={ping_type.value} and schedule_type=\'{event_type}\' and tag={tag}')
        self.load()

    async def get_mention_string(self, ping_type: GuildPingType, event_type: str) -> str:
        result = ''
        guild = self.client.get_guild(self.key)
        if guild is None: return ''
        await guild.fetch_roles()
        for ping in self.get(ping_type, event_type):
            role = guild.get_role(ping.tag)
            if role:
                result += f'{role.mention} '
        return result.strip()
