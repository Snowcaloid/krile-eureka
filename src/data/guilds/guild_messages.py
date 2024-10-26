from typing import List

from data.db.sql import SQL, Record
from data.guilds.guild_message_functions import GuildMessageFunction

class GuildMessage:
    id: int
    channel_id: int
    message_id: int
    function: GuildMessageFunction
    event_type: str

    def load(self, id: int) -> None:
        record = SQL('guild_messages').select(fields=['channel_id', 'message_id', 'event_type', 'function'],
                                              where=f'id={id}')
        if record:
            self.id = id
            self.channel_id = record['channel_id']
            self.message_id = record['message_id']
            self.event_type = record['event_type']
            self.function = GuildMessageFunction(record['function'])

class GuildMessages:
    _list: List[GuildMessage] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self._list.clear()
        for record in SQL('guild_messages').select(fields=['id'],
                                                   where=f'guild_id={guild_id}',
                                                   all=True):
            channel = GuildMessage()
            channel.load(record['id'])
            self._list.append(channel)

    def get(self, function: GuildMessageFunction = GuildMessageFunction.NONE, event_type: str = '') -> GuildMessage:
        for message_data in self._list:
            if message_data.function == function and message_data.event_type == event_type:
                return message_data
        return None

    def get_by_message_id(self, message_id: int) -> GuildMessage:
        for message_data in self._list:
            if message_data.message_id == message_id:
                return message_data
        return None

    def add(self, message_id: int, channel_id: int, function: GuildMessageFunction, event_type: str = '') -> None:
        SQL('guild_messages').insert(Record(guild_id=self.guild_id, channel_id=channel_id, function=function.value, event_type=event_type, message_id=message_id))
        self.load(self.guild_id)

    def remove(self, message_id: int) -> None:
        SQL('guild_messages').delete(f'guild_id={self.guild_id} and message_id={message_id}')
        self.load(self.guild_id)