import bot
from typing import List

from data.events.event import Event, EventCategory
from data.guilds.guild_channel_functions import GuildChannelFunction

class GuildChannel:
    id: int = -1
    event_type: str = ''
    function: GuildChannelFunction = GuildChannelFunction.NONE

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select channel_id, event_type, function from channels where id={id}')
            if record:
                self.id = record[0]
                self.event_type = record[1]
                self.function = GuildChannelFunction(record[2])
        finally:
            db.disconnect()

class GuildChannels:
    _list: List[GuildChannel] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self._list.clear()
            records = db.query(f'select id from channels where guild_id={guild_id}')
            for record in records:
                channel = GuildChannel()
                channel.load(record[0])
                self._list.append(channel)
        finally:
            db.disconnect()

    def get(self, function: GuildChannelFunction = GuildChannelFunction.NONE, event_type: str = '') -> GuildChannel:
        for channel in self._list:
            if channel.function == function and event_type == event_type:
                return channel
        return None

    def add(self, id: int, function: GuildChannelFunction, event_type: str = '') -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'insert into channels (guild_id, function, event_type, channel_id) values ({str(self.guild_id)}, {str(function.value)}, \'{event_type}\', {str(id)})')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def set(self, id: int, function: GuildChannelFunction, event_type: str = '') -> None:
        if self.get(function, event_type):
            db = bot.instance.data.db
            db.connect()
            try:
                db.query(f'update channels set channel_id={id} where guild_id={str(self.guild_id)} and function={{str(function.value)}} and event_type=\'{event_type}\'')
                self.load(self.guild_id)
            finally:
                db.disconnect()
        else:
            self.add(id, function, event_type)

    def set_category(self, id: int, function: GuildChannelFunction, event_category: EventCategory):
        db = bot.instance.data.db
        db.connect()
        try:
            for event_base in Event.all_events_for_category(event_category):
                self.set(id, function, event_base.type())
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def remove(self, function: GuildChannelFunction, event_type: str = '') -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            event_type_part = f'and event_type=\'{event_type}\'' if event_type else ''
            db.query(f'delete from channels where guild_id={str(self.guild_id)} and function={str(function.value)} {event_type_part}')
            self.load(self.guild_id)
        finally:
            db.disconnect()