from json import loads
from typing import List

from data.db.sql import SQL, Record
from data.events.event_template import EventTemplate


class GuildEventTemplates:
    _list: List[EventTemplate] = []
    _default_templates: List[EventTemplate] = []

    guild_id: int

    def __init__(self, default_templates: List[EventTemplate] = []):
        self._default_templates = default_templates

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self._list.clear()
        self._list.extend(self._default_templates)
        for record in SQL('event_templates').select(fields=['data'], where=f'guild_id={guild_id}', all=True):
            data = record['data']
            template = EventTemplate(loads(data))
            self._list.append(template)

    def get(self, event_type: str) -> EventTemplate:
        return next((template for template in self._list if template.type() == event_type), None)

    def add(self, event_type: str, template: EventTemplate) -> None:
        SQL('event_templates').insert(Record(guild_id=self.guild_id, event_type=event_type, data=template.data))
        self.load(self.guild_id)

    def set(self, event_type: str, template: EventTemplate) -> None:
        if self.get(event_type):
            SQL('event_templates').update(Record(data=template.data), f"event_type='{event_type}'")
            self.load(self.guild_id)
        else:
            self.add(id, event_type, template)

    def remove(self, event_type: str) -> None:
        SQL('event_templates').delete(f"guild_id={self.guild_id} and event_type='{event_type}'")
        self.load(self.guild_id)