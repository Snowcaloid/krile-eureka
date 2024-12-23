from typing import Dict
from discord import Message, NotFound, TextChannel


class MessageCache:
    cache: Dict[int, Message]

    def __init__(self) -> None:
        self.cache = {}

    async def get(self, id: int, channel: TextChannel) -> Message:
        message = self.cache.get(id, None)
        if message: return message
        try:
            message = await channel.fetch_message(id)
        except NotFound:
            message = None

        self.cache.update({id: message})
        return message

messages = MessageCache()