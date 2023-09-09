from typing import Dict
from discord import Message, TextChannel


class MessageCache:
    cache: Dict[int, Message]

    def __init__(self) -> None:
        self.cache = {}

    async def get(self, id: int, channel: TextChannel) -> Message:
        for message_id in self.cache:
            if message_id == id:
                return self.cache[id]
        message = await channel.fetch_message(id)
        self.cache.update({id: message})
        return message

messages = MessageCache()