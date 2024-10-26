from typing import List

from data.db.sql import SQL, Record
from data.events.event import Event, EventCategory
from data.guilds.guild_channel_functions import GuildChannelFunction

class GuildChannel:
    id: int = -1
    event_type: str = ''
    function: GuildChannelFunction = GuildChannelFunction.NONE

    def load(self, id: int) -> None:
        record = SQL('channels').select(fields=['channel_id', 'event_type', 'function'], where=f'id={id}')
        if record:
            self.id = record['channel_id']
            self.event_type = record['event_type']
            self.function = GuildChannelFunction(record['function'])

class GuildChannels:
    _list: List[GuildChannel] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self._list.clear()
        for record in SQL('channels').select(fields=['id'], where=f'guild_id={guild_id}', all=True):
            channel = GuildChannel()
            channel.load(record['id'])
            self._list.append(channel)

    def get(self, function: GuildChannelFunction = GuildChannelFunction.NONE, event_type: str = '') -> GuildChannel:
        for channel in self._list:
            if channel.function == function and channel.event_type == event_type:
                return channel
        return None

    def add(self, id: int, function: GuildChannelFunction, event_type: str = '') -> None:
        SQL('channels').insert(Record(guild_id=self.guild_id, function=function.value, event_type=event_type, channel_id=id))
        self.load(self.guild_id)

    def set(self, id: int, function: GuildChannelFunction, event_type: str = '') -> None:
        if self.get(function, event_type):
            SQL('channels').update(Record(channel_id=id), f'guild_id={self.guild_id} and function={function.value} and event_type=\'{event_type}\'')
            self.load(self.guild_id)
        else:
            self.add(id, function, event_type)

    def set_category(self, id: int, function: GuildChannelFunction, event_category: EventCategory):
        query = Record() # Prevent multiple connects and disconnects
        for event_base in Event.all_events_for_category(event_category):
            self.set(id, function, event_base.type())
        self.load(self.guild_id)
        del query

    def remove(self, function: GuildChannelFunction, event_type: str = '') -> None:
        event_type_part = f'and event_type=\'{event_type}\'' if event_type else ''
        SQL('channels').delete(f'guild_id={self.guild_id} and function={function.value} {event_type_part}')
        self.load(self.guild_id)