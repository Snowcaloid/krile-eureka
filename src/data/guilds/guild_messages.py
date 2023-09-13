import bot
from typing import List

from data.guilds.guild_message_functions import GuildMessageFunction

class GuildMessage:
    id: int
    channel_id: int
    message_id: int
    function: GuildMessageFunction
    event_type: str

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select channel_id, message_id, event_type, function from guild_messages where id={id}')
            if record:
                self.id = id
                self.channel_id = record[0][0]
                self.message_id = record[0][1]
                self.event_type = record[0][2]
                self.function = GuildMessageFunction(record[0][3])
        finally:
            db.disconnect()

class GuildMessages:
    _list: List[GuildMessage] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self._list.clear()
            records = db.query(f'select id from guild_messages where guild_id={guild_id}')
            for record in records:
                channel = GuildMessage()
                channel.load(record[0])
                self._list.append(channel)
        finally:
            db.disconnect()

    def get(self, function: GuildMessageFunction = GuildMessageFunction.NONE, event_type: str = '') -> GuildMessage:
        for message_data in self._list:
            if message_data.function == function and message_data.event_type == event_type:
                return message_data
        return None

    def add(self, message_id: int, channel_id: int, function: GuildMessageFunction, event_type: str = '') -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'insert into guild_messages (guild_id, channel_id, function, event_type, message_id) values ({str(self.guild_id)}, {str(channel_id)}, {str(function.value)}, \'{event_type}\', {str(message_id)})')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def remove(self, message_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from guild_messages where guild_id={str(self.guild_id)} and message_id={message_id}')
            self.load(self.guild_id)
        finally:
            db.disconnect()