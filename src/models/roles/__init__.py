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
    event_type: str = None
    function: GuildRoleFunction = None

    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def to_record(self) -> Record:
        record = Record()
        if self.guild_id is not None:
            record['guild_id'] = self.guild_id
        if self.id is not None:
            record['id'] = self.id
        if self.role_id is not None:
            record['role_id'] = self.role_id
        if self.event_type is not None:
            record['event_type'] = self.event_type
        if self.function is not None:
            record['function'] = self.function.value if self.function else None
        return record

    @classmethod
    def from_record(cls, record: Record) -> RoleStruct:
        return RoleStruct(
            guild_id=record['guild_id'],
            id=record['id'],
            role_id=record['role_id'],
            event_type=record['event_type'],
            function=GuildRoleFunction(record['function']) if record['function'] else None
        )

    @override
    def intersect(self, other: RoleStruct) -> RoleStruct:
        return RoleStruct(
            guild_id=other.guild_id or self.guild_id,
            id=other.id or self.id,
            role_id=other.role_id or self.role_id,
            event_type=other.event_type or self.event_type,
            function=other.function or self.function
        )

    @override
    def __eq__(self, other: RoleStruct) -> bool:
        if other.id and self.id:
            return self.id == other.id
        return (other.guild_id is None or self.guild_id == other.guild_id) and \
            (other.role_id is None or self.role_id == other.role_id) and \
            (other.event_type is None or self.event_type == other.event_type) and \
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
        if self.event_type is not None:
            result.append(f"Event Type: {self.event_type}")
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
            'role': {
                'id': str(self.role_id),
                'name': self._bot.client.get_guild(self.guild_id).get_role(self.role_id).name
            },
            'event_type': self.event_type,
            'function': self.function.name
        }