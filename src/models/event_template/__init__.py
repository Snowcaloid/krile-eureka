from __future__ import annotations

from dataclasses import dataclass
from typing import override
from models._base import BaseStruct
from models.event_template.data import EventTemplateData
from utils.basic_types import Unassigned

@dataclass
class EventTemplateStruct(BaseStruct):
    guild_id: int = Unassigned #type: ignore
    event_type: str = Unassigned #type: ignore
    data: EventTemplateData = Unassigned #type: ignore

    @classmethod
    def db_table_name(cls) -> str: return 'event_templates'

    @override
    def type_name(self) -> str: return 'event template'

    @override
    def identity(self) -> EventTemplateStruct:
        return EventTemplateStruct(guild_id=self.guild_id, event_type=self.event_type)

    @override
    def fixup_types(self) -> None:
        if isinstance(self.data, dict):
            self.data = EventTemplateData.from_json(self.data)

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.guild_id, int):
            result.append(f'Guild ID: {self.guild_id}')
        if isinstance(self.event_type, str):
            result.append(f'Event Type: {self.event_type}')
        if isinstance(self.data, EventTemplateData):
            result.append(f'Data: {self.data}')
        return f'EventTemplateStruct({', '.join(result)})' if result else 'No event template data available.'

    @override
    def changes_since(self, other: EventTemplateStruct) -> str:
        return 'changes_since not implemented for EventTemplateStruct'

    @override
    def marshal(self) -> dict:
        return {
            'guild_id': self.marshal_value(self.guild_id),
            'event_type': self.marshal_value(self.event_type),
            'data': self.marshal_value(self.data.source)
        }