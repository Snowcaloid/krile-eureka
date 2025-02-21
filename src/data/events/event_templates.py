from bindable import Bindable
from data.db.sql import SQL, Record
from data.events.event_category import EventCategory
from data.events.event_template import CustomEventTamplate, EventTemplate

from typing import List, Union

class EventTemplates(Bindable):
    _list: List[Union[EventTemplate, CustomEventTamplate]]

    from data.events.default_event_templates import DefaultEventTemplates
    @DefaultEventTemplates.bind
    def default_templates(self) -> DefaultEventTemplates: ...

    def __init__(self):
        self._list = []

    def load(self) -> None:
        self._list.clear()
        self._list.extend(self.default_templates.loaded_assets)
        for record in SQL('event_templates').select(fields=['guild_id', 'data'], all=True):
            self._list.append(CustomEventTamplate(record['guild_id'], record['data']))

    def all(self, guild_id: int) -> List[EventTemplate]:
        return [template for template in self._list if not isinstance(template, CustomEventTamplate) or template.guild_id == guild_id]

    def get(self, guild_id: int, event_type: str) -> EventTemplate:
        return next((template for template in self.all(guild_id) if template.type() == event_type), None)

    def get_by_categories(self, guild_id: int, categories: List[EventCategory]) -> List[EventTemplate]:
        return [template for template in self.all(guild_id) if template.category() in categories]

    def add(self, guild_id: int, event_type: str, template: EventTemplate) -> None:
        SQL('event_templates').insert(Record(guild_id=guild_id, event_type=event_type, data=template.data))
        self.load(self.guild_id)

    def set(self, guild_id: int, event_type: str, template: EventTemplate) -> None:
        if self.get(guild_id, event_type):
            SQL('event_templates').update(Record(data=template.data), f"event_type='{event_type}' and guild_id={guild_id}")
            self.load()
        else:
            self.add(guild_id, event_type, template)

    def remove(self, guild_id: int, event_type: str) -> None:
        SQL('event_templates').delete(f"guild_id={guild_id} and event_type='{event_type}'")
        self.load()