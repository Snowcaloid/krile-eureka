from __future__ import annotations
from dataclasses import dataclass
from typing import override

from discord import ButtonStyle
from models._base import BaseStruct
from utils.basic_types import ButtonType, Unassigned
from utils.functions import fix_enum

@dataclass
class ButtonStruct(BaseStruct):
    button_id: str = Unassigned #type: ignore
    button_type: ButtonType = Unassigned #type: ignore
    channel_id: int = Unassigned #type: ignore
    channel_name: str = Unassigned #type: ignore
    message_id: int = Unassigned #type: ignore
    emoji: str = Unassigned #type: ignore
    label: str = Unassigned #type: ignore
    style: ButtonStyle = Unassigned #type: ignore
    row: int = Unassigned #type: ignore
    index: int = Unassigned #type: ignore
    role_id: int = Unassigned #type: ignore
    party: int = Unassigned #type: ignore
    event_id: int = Unassigned #type: ignore

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(ButtonType, self.button_type)
        assert isinstance(fixed_enum, ButtonType), f"Invalid ButtonType: {self.button_type}"
        self.button_type = fixed_enum
        fixed_enum = fix_enum(ButtonStyle, self.style)
        assert isinstance(fixed_enum, ButtonStyle), f"Invalid ButtonStyle: {self.style}"
        self.style = fixed_enum

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.button_id, int):
            result.append(f'ID: {self.button_id}')
        if isinstance(self.button_type, ButtonType):
            result.append(f'Type: {self.button_type.name}')
        if isinstance(self.channel_id, int):
            result.append(f'Channel: {self.channel_id}')
        if isinstance(self.channel_name, str):
            result.append(f'Channel Name: {self.channel_name}')
        if isinstance(self.message_id, int):
            result.append(f'Message: {self.message_id}')
        if isinstance(self.emoji, str):
            result.append(f'Emoji: {self.emoji}')
        if isinstance(self.label, str):
            result.append(f'Label: {self.label}')
        if isinstance(self.style, ButtonStyle):
            result.append(f'Style: {self.style.name}')
        if isinstance(self.row, int):
            result.append(f'Row: {self.row}')
        if isinstance(self.index, int):
            result.append(f'Index: {self.index}')
        if isinstance(self.role_id, int):
            result.append(f'Role: {self.role_id}')
        if isinstance(self.party, int):
            result.append(f'Party: {self.party}')
        if isinstance(self.event_id, int):
            result.append(f'Event: {self.event_id}')
        return f'ButtonStruct({", ".join(result)})'

    @override
    def changes_since(self, other: ButtonStruct) -> str:
        changes = []
        if isinstance(self.button_id, str) and self.button_id != other.button_id:
            changes.append(f'ID: {other.button_id} -> {self.button_id}')
        if isinstance(self.button_type, ButtonType) and self.button_type != other.button_type:
            changes.append(f'Type: {other.button_type.name} -> {self.button_type.name}')
        if isinstance(self.channel_id, int) and self.channel_id != other.channel_id:
            changes.append(f'Channel: {other.channel_id} -> {self.channel_id}')
        if isinstance(self.channel_name, str) and self.channel_name != other.channel_name:
            changes.append(f'Channel Name: {other.channel_name} -> {self.channel_name}')
        if isinstance(self.message_id, int) and self.message_id != other.message_id:
            changes.append(f'Message: {other.message_id} -> {self.message_id}')
        if isinstance(self.emoji, str) and self.emoji != other.emoji:
            changes.append(f'Emoji: {other.emoji} -> {self.emoji}')
        if isinstance(self.label, str) and self.label != other.label:
            changes.append(f'Label: {other.label} -> {self.label}')
        if isinstance(self.style, ButtonStyle) and self.style != other.style:
            changes.append(f'Style: {other.style.name} -> {self.style.name}')
        if isinstance(self.row, int) and self.row != other.row:
            changes.append(f'Row: {other.row} -> {self.row}')
        if isinstance(self.index, int) and self.index != other.index:
            changes.append(f'Index: {other.index} -> {self.index}')
        if isinstance(self.role_id, int) and self.role_id != other.role_id:
            changes.append(f'Role: {other.role_id} -> {self.role_id}')
        if isinstance(self.party, int) and self.party != other.party:
            changes.append(f'Party: {other.party} -> {self.party}')
        if isinstance(self.event_id, int) and self.event_id != other.event_id:
            changes.append(f'Event: {other.event_id} -> {self.event_id}')
        if not changes:
            return 'No changes'
        return '\n'.join(changes)

    @override
    def marshal(self) -> dict:
        return {
            'button_id': self.marshal_value(self.button_id),
            'button_type': self.marshal_value(self.button_type),
            'channel': {
                'id': self.marshal_value(self.channel_id),
                'name': self.marshal_value(self.channel_name)
            },
            'message_id': self.marshal_value(self.message_id),
            'emoji': self.marshal_value(self.emoji),
            'label': self.marshal_value(self.label),
            'style': self.marshal_value(self.style),
            'row': self.marshal_value(self.row),
            'index': self.marshal_value(self.index),
            'role_id': self.marshal_value(self.role_id),
            'party': self.marshal_value(self.party),
            'event_id': self.marshal_value(self.event_id)
        }
