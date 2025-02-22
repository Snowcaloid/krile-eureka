from typing import List

from centralized_data import GlobalCollection

from data.db.sql import SQL, Record
from basic_types import GuildID, GuildMessageFunction

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

class GuildMessages(GlobalCollection[GuildID]):
    _list: List[GuildMessage]

    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('guild_messages').select(fields=['id'],
                                                   where=f'guild_id={self.key}',
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
        SQL('guild_messages').insert(Record(guild_id=self.key, channel_id=channel_id, function=function.value, event_type=event_type, message_id=message_id))
        self.load()

    def remove(self, message_id: int) -> None:
        SQL('guild_messages').delete(f'guild_id={self.key} and message_id={message_id}')
        self.load()