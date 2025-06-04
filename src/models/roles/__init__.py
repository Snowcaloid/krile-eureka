from __future__ import annotations
from typing import override
from bot import Bot
from data.db.sql import Record
from models._base import BaseStruct
from utils.basic_types import GuildRoleFunction

from dataclasses import dataclass


@dataclass
class RoleStruct(BaseStruct):
    guild_id: int = None
    id: int = None
    role_id: int = None
    event_category: str = None
    function: GuildRoleFunction = None

    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def __eq__(self, other: RoleStruct) -> bool:
        if other.id and self.id:
            return self.id == other.id
        return (other.guild_id is None or self.guild_id == other.guild_id) and \
            (other.role_id is None or self.role_id == other.role_id) and \
            (other.event_category is None or self.event_category == other.event_category) and \
            (other.function is None or self.function == other.function)

    @override
    def __repr__(self) -> str:
        result = []
        if self.guild_id is not None:
            result.append(f"Guild ID: {self.guild_id}")
        if self.id is not None:
            result.append(f"ID: {self.id}")
        if self.role_id is not None:
            role_name = self._bot.client.get_guild(self.guild_id).get_role(self.role_id).name if self.role_id else 'Unknown'
            result.append(f"Role: @{role_name} ({str(self.role_id)})")
        if self.event_category is not None:
            result.append(f"Event Type: {self.event_category}")
        if self.function is not None:
            result.append(f"Function: {self.function.name}")
        return ', '.join(result)

    @override
    def changes_since(self, other: RoleStruct) -> str:
        result = []
        if other.id != self.id:
            result.append(f"ID: {other.id} -> {self.id}")
        if other.role_id != self.role_id:
            role_name = self._bot.client.get_guild(self.guild_id).get_role(self.role_id).name if self.role_id else 'Unknown'
            other_role_name = self._bot.client.get_guild(self.guild_id).get_role(other.role_id).name if other.role_id else 'Unknown'
            result.append(f"Role: @{other_role_name} ({str(other.role_id)}) -> #{role_name} ({str(self.role_id)})")
        if other.event_category != self.event_category:
            result.append(f"Event Type: {other.event_category} -> {self.event_category}")
        if other.function != self.function:
            result.append(f"Function: {other.function.name} -> {self.function.name}")
        if not result:
            return "No changes"

    def marshal(self) -> dict:
        return {
            'guild_id': str(self.guild_id),
            'id': str(self.id),
            'role': {
                'id': str(self.role_id),
                'name': self._bot.client.get_guild(self.guild_id).get_role(self.role_id).name
            },
            'event_category': self.event_category,
            'function': self.function.name
        }