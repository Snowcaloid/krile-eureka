from __future__ import annotations
from dataclasses import dataclass
from typing import override
from bot import Bot
from data.db.sql import Record, enum_db_value
from models._base import BaseStruct
from utils.basic_types import Unassigned, GuildChannelFunction


@dataclass
class ChannelStruct(BaseStruct):
    guild_id: int = Unassigned
    id: int = Unassigned
    channel_id: int = Unassigned
    event_type: str = Unassigned
    function: GuildChannelFunction = Unassigned

    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def __eq__(self, other: ChannelStruct) -> bool:
        if other.id and self.id:
            return self.id == other.id
        return (other.guild_id is None or self.guild_id == other.guild_id) and \
            (other.channel_id is None or self.channel_id == other.channel_id) and \
            (other.event_type is None or self.event_type == other.event_type) and \
            (other.function is None or self.function == other.function)

    @override
    def __repr__(self) -> str:
        result = []
        if self.guild_id is not None:
            result.append(f"Guild ID: {self.guild_id}")
        if self.id is not None:
            result.append(f"ID: {self.id}")
        if self.channel_id is not None:
            channel_name = self._bot.client.get_channel(self.channel_id).name if self.channel_id else 'Unknown'
            result.append(f"Channel: #{channel_name} ({str(self.channel_id)})")
        if self.event_type is not None:
            result.append(f"Event Type: {self.event_type}")
        if self.function is not None:
            result.append(f"Function: {self.function.name}")
        return ', '.join(result)

    @override
    def changes_since(self, other: ChannelStruct) -> str:
        result = []
        if other.id != self.id:
            result.append(f"ID: {other.id} -> {self.id}")
        if other.channel_id != self.channel_id:
            channel_name = self._bot.client.get_channel(self.channel_id).name if self.channel_id else 'Unknown'
            other_channel_name = self._bot.client.get_channel(other.channel_id).name if other.channel_id else 'Unknown'
            result.append(f"Channel: #{other_channel_name} ({str(other.channel_id)}) -> #{channel_name} ({str(self.channel_id)})")
        if other.event_type != self.event_type:
            result.append(f"Event Type: {other.event_type} -> {self.event_type}")
        if other.function != self.function:
            result.append(f"Function: {other.function.name} -> {self.function.name}")
        if not result:
            return "No changes"

    def marshal(self) -> dict:
        return {
            'guild_id': str(self.guild_id),
            'id': str(self.id),
            'channel': {
                'id': str(self.channel_id),
                'name': self._bot.client.get_channel(self.channel_id).name
            },
            'event_type': self.event_type,
            'function': self.function.name
        }