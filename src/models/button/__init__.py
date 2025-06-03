from __future__ import annotations
from dataclasses import dataclass
from typing import override

from discord import Button, ButtonStyle
from data.db.sql import Record
from models._base import BaseStruct
from utils.basic_types import ButtonType

@dataclass
class ButtonStruct(BaseStruct):
    button_id: str = None
    button_type: ButtonType
    channel_id: int = None
    message_id: int = None
    emoji: str = None
    label: str = None
    style: ButtonStyle = None
    row: int = None
    index: int = None
    role_id: int = None
    party: int = None
    event_id: int = None

    @override
    def to_record(self) -> Record:
        record = Record()
        if self.button_id is not None:
            record['id'] = self.button_id
        if self.button_type is not None:
            record['button_type'] = self.button_type.value
        if self.channel_id is not None:
            record['channel_id'] = self.channel_id
        if self.message_id is not None:
            record['message_id'] = self.message_id
        if self.emoji is not None:
            record['emoji'] = self.emoji
        if self.label is not None:
            record['label'] = self.label
        if self.style is not None:
            record['style'] = self.style.value
        if self.row is not None:
            record['row'] = self.row
        if self.index is not None:
            record['index'] = self.index
        if self.role_id is not None:
            record['role'] = self.role_id
        if self.party is not None:
            record['party'] = self.party
        if self.event_id is not None:
            record['event_id'] = self.event_id
        return record

    @classmethod
    def from_record(cls, record: Record) -> ButtonStruct:
        kwargs = {k : v for k, v in record.items() if v is not None}
        if kwargs.get('button_type'):
            kwargs['button_type'] = ButtonType(kwargs['button_type'])
        if kwargs.get('style'):
            kwargs['style'] = ButtonStyle(kwargs['style'])
        return ButtonStruct(**kwargs)

    @override
    def intersect(self, other: ButtonStruct) -> ButtonStruct:
        id = other.button_id if hasattr(other, 'id') else self.button_id
        button_type = other.button_type if hasattr(other, 'button_type') else self.button_type
        channel_id = other.channel_id if hasattr(other, 'channel_id') else self.channel_id
        message_id = other.message_id if hasattr(other, 'message_id') else self.message_id
        emoji = other.emoji if hasattr(other, 'emoji') else self.emoji
        label = other.label if hasattr(other, 'label') else self.label
        style = other.style if hasattr(other, 'style') else self.style
        row = other.row if hasattr(other, 'row') else self.row
        index = other.index if hasattr(other, 'index') else self.index
        role = other.role_id if hasattr(other, 'role') else self.role_id
        party = other.party if hasattr(other, 'party') else self.party
        event_id = other.event_id if hasattr(other, 'event_id') else self.event_id
        return ButtonStruct(
            button_id=id,
            button_type=button_type,
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
            label=label,
            style=style,
            row=row,
            index=index,
            role_id=role,
            party=party,
            event_id=event_id
        )

    # TODO: Implement the following methods
    # tostring
    #equals
    #marshal : tojson
    #changes_since : diffrerence between 2 objects