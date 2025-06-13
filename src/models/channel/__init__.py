from __future__ import annotations
from dataclasses import dataclass
from typing import override
from bot import Bot
from models._base import BaseStruct
from utils.basic_types import Unassigned, GuildChannelFunction, fix_enum


@dataclass
class ChannelStruct(BaseStruct):
    guild_id: int = Unassigned #type: ignore
    id: int = Unassigned #type: ignore
    channel_id: int = Unassigned #type: ignore
    event_type: str = Unassigned #type: ignore
    function: GuildChannelFunction = Unassigned #type: ignore

    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(GuildChannelFunction, self.function)
        assert isinstance(fixed_enum, GuildChannelFunction), f"Invalid GuildChannelFunction: {self.function}"
        self.function = fixed_enum

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.guild_id, int):
            result.append(f"Guild ID: {self.guild_id}")
        if isinstance(self.id, int):
            result.append(f"ID: {self.id}")
        if isinstance(self.channel_id, int):
            channel_name = self._bot.get_text_channel(self.channel_id).name if self.channel_id else 'Unknown'
            result.append(f"Channel: #{channel_name} ({str(self.channel_id)})")
        if isinstance(self.event_type, str):
            result.append(f"Event Type: {self.event_type}")
        if isinstance(self.function, GuildChannelFunction):
            result.append(f"Function: {self.function.name}")
        return ', '.join(result)

    @override
    def changes_since(self, other: ChannelStruct) -> str:
        result = []
        if isinstance(self.id, int) and other.id != self.id:
            result.append(f"ID: {other.id} -> {self.id}")
        if isinstance(self.channel_id, int) and other.channel_id != self.channel_id:
            channel_name = self._bot.get_text_channel(self.channel_id).name if self.channel_id else 'Unknown'
            other_channel_name = self._bot.get_text_channel(other.channel_id).name if other.channel_id else 'Unknown'
            result.append(f"Channel: #{other_channel_name} ({str(other.channel_id)}) -> #{channel_name} ({str(self.channel_id)})")
        if isinstance(self.event_type, str) and other.event_type != self.event_type:
            result.append(f"Event Type: {other.event_type} -> {self.event_type}")
        if isinstance(self.function, GuildChannelFunction) and other.function != self.function:
            result.append(f"Function: {other.function.name} -> {self.function.name}")
        if not result:
            return "No changes"
        return '\n'.join(result)

    def marshal(self) -> dict:
        return {
            'guild_id': str(self.guild_id),
            'id': str(self.id),
            'channel': {
                'id': str(self.channel_id),
                'name': self._bot.get_text_channel(self.channel_id).name
            },
            'event_type': self.event_type,
            'function': self.function.name
        }