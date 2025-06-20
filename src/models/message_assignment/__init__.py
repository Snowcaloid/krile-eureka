from __future__ import annotations

from dataclasses import dataclass
from typing import override
from models._base import BaseStruct, Unassigned
from utils.basic_types import MessageFunction
from utils.functions import fix_enum


@dataclass
class MessageAssignmentStruct(BaseStruct):
    id: int = Unassigned #type: ignore
    guild_id: int = Unassigned #type: ignore
    guild_name: str = Unassigned #type: ignore
    channel_id: int = Unassigned #type: ignore
    channel_name: str = Unassigned #type: ignore
    message_id: int = Unassigned #type: ignore
    function: MessageFunction = Unassigned #type: ignore

    @classmethod
    def db_table_name(cls) -> str: return 'message_assignments'

    @override
    def type_name(self) -> str: return 'message assignment'

    @override
    def identity(self) -> MessageAssignmentStruct: return self # Currently, all fields are part of the identity

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(MessageFunction, self.function)
        assert isinstance(fixed_enum, MessageFunction), f"Invalid MessageFunction: {self.function}"
        self.function = fixed_enum

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.id, int):
            result.append(f'ID: {self.id}')
        if isinstance(self.guild_id, int):
            result.append(f'Guild ID: {self.guild_id}')
        if isinstance(self.guild_name, str):
            result.append(f'Guild Name: {self.guild_name}')
        if isinstance(self.channel_id, int):
            result.append(f'Channel ID: {self.channel_id}')
        if isinstance(self.channel_name, str):
            result.append(f'Channel Name: {self.channel_name}')
        if isinstance(self.message_id, int):
            result.append(f'Message ID: {self.message_id}')
        if isinstance(self.function, MessageFunction):
            result.append(f'Function: {self.function.name}')
        return ', '.join(result)

    @override
    def changes_since(self, other: MessageAssignmentStruct) -> str:
        changes = []
        if isinstance(self.id, int) and self.id != other.id:
            changes.append(f'Guild ID: {other.guild_id} -> {self.guild_id}')
        if isinstance(self.guild_id, int) and self.guild_id != other.guild_id:
            changes.append(f'Guild ID: {other.guild_id} -> {self.guild_id}')
        if isinstance(self.guild_name, str) and self.guild_name != other.guild_name:
            changes.append(f'Guild Name: {other.guild_name} -> {self.guild_name}')
        if isinstance(self.channel_id, int) and self.channel_id != other.channel_id:
            changes.append(f'Channel ID: {other.channel_id} -> {self.channel_id}')
        if isinstance(self.channel_name, str) and self.channel_name != other.channel_name:
            changes.append(f'Channel Name: {other.channel_name} -> {self.channel_name}')
        if isinstance(self.message_id, int) and self.message_id != other.message_id:
            changes.append(f'Message ID: {other.message_id} -> {self.message_id}')
        if isinstance(self.function, MessageFunction) and self.function != other.function:
            changes.append(f'Function: {other.function.name} -> {self.function.name}')
        return ', '.join(changes) if changes else 'No changes'

    @override
    def marshal(self) -> dict:
        return {
            'id': self.marshal_value(self.id),
            'guild': {
                'id': self.marshal_value(self.guild_id),
                'name': self.marshal_value(self.guild_name)
            },
            'channel': {
                'id': self.marshal_value(self.channel_id),
                'name': self.marshal_value(self.channel_name)
            },
            'message_id': self.marshal_value(self.message_id),
            'function': self.marshal_value(self.function.name)
        }