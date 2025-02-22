from typing import Dict, override
from centralized_data import Bindable
from discord import Message, NotFound, TextChannel


class MessageCache(Bindable):
    _cache: Dict[int, Message]

    @classmethod
    def provider_name(cl) -> str:
        return 'message_cache'

    @override
    def constructor(self) -> None:
        self._cache = {}

    async def get(self, id: int, channel: TextChannel) -> Message:
        message = self._cache.get(id, None)
        if message: return message
        try:
            message = await channel.fetch_message(id)
        except NotFound:
            message = None

        self._cache.update({id: message})
        return message

    def remove(self, id: int) -> None:
        self._cache.pop(id, None)

    def clear(self) -> None:
        self._cache.clear()