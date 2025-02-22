from typing import List, override

from centralized_data import GlobalCollection

from data.db.sql import SQL, Record
from data.events.event_category import EventCategory
from basic_types import GuildChannelFunction, GuildID
from data.events.event_templates import EventTemplates

class GuildChannel:
    id: int
    event_type: str
    function: GuildChannelFunction

    def load(self, id: int) -> None:
        record = SQL('channels').select(fields=['channel_id', 'event_type', 'function'], where=f'id={id}')
        if record:
            self.id = record['channel_id']
            self.event_type = record['event_type']
            self.function = GuildChannelFunction(record['function'])

class GuildChannels(GlobalCollection[GuildID]):
    _list: List[GuildChannel]

    @override
    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('channels').select(fields=['id'], where=f'guild_id={self.key}', all=True):
            channel = GuildChannel()
            channel.load(record['id'])
            self._list.append(channel)

    def get(self, function: GuildChannelFunction = GuildChannelFunction.NONE, event_type: str = '') -> GuildChannel:
        for channel in self._list:
            if channel.function == function and channel.event_type == event_type:
                return channel
        return None

    def add(self, id: int, function: GuildChannelFunction, event_type: str = '') -> None:
        SQL('channels').insert(Record(guild_id=self.key, function=function.value, event_type=event_type, channel_id=id))
        self.load()

    def set(self, id: int, function: GuildChannelFunction, event_type: str = '') -> None:
        if self.get(function, event_type):
            SQL('channels').update(Record(channel_id=id), f'guild_id={self.key} and function={function.value} and event_type=\'{event_type}\'')
            self.load()
        else:
            self.add(id, function, event_type)

    def set_category(self, id: int, function: GuildChannelFunction, event_category: EventCategory):
        query = Record() # Prevent multiple connects and disconnects
        for event_template in EventTemplates(self.key).get_by_categories([event_category]):
            self.set(id, function, event_template.type())
        self.load()
        del query

    def remove(self, function: GuildChannelFunction, event_type: str = '') -> None:
        event_type_part = f'and event_type=\'{event_type}\'' if event_type else ''
        SQL('channels').delete(f'guild_id={self.key} and function={function.value} {event_type_part}')
        self.load()