from centralized_data import GlobalCollection
from discord import Interaction
from discord.app_commands import Choice
from data.validation.permission_validator import PermissionValidator
from utils.basic_types import GuildID
from data.db.sql import SQL, Record
from data.events.event_category import EventCategory
from data.events.event_template import EventTemplate

from typing import List, override

from utils.functions import filter_choices_by_current

class EventTemplates(GlobalCollection[GuildID]):
    _list: List[EventTemplate]

    from data.events.default_event_templates import DefaultEventTemplates
    @DefaultEventTemplates.bind
    def default_templates(self) -> DefaultEventTemplates: ...

    @override
    def constructor(self, key: GuildID = None):
        super().constructor(key)
        self._list = []
        self.load()

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        self._list.extend(self.default_templates.loaded_assets)
        for record in SQL('event_templates').select(fields=['data'], where=f'guild_id={self.key}', all=True):
            event_template = EventTemplate('')
            event_template.source = record['data']
            self._list.append(event_template)

    @property
    def all(self) -> List[EventTemplate]:
        return self._list

    def get(self, event_type: str) -> EventTemplate:
        return next((template for template in self._list if template.type() == event_type), None)

    def get_by_categories(self, categories: List[EventCategory]) -> List[EventTemplate]:
        return [template for template in self._list if template.category() in categories]

    @classmethod
    def autocomplete(cls, interaction: Interaction, current: str) -> List[Choice]:
        allowed_categories = PermissionValidator().get_raid_leader_permissions(interaction.user)
        return filter_choices_by_current([
            event_template.as_choice() for event_template in cls(interaction.guild_id).get_by_categories(allowed_categories)], current)

    @classmethod
    def autocomplete_with_categories(cls, current: str, guild_id: int) -> List[Choice]:
        return filter_choices_by_current(EventCategory.all_category_choices() + [
            event_template.as_choice() for event_template in cls(guild_id).all], current)

    def add(self, event_type: str, template: EventTemplate) -> None:
        SQL('event_templates').insert(Record(guild_id=self.key, event_type=event_type, data=template.data))
        self.load()

    def set(self, event_type: str, template: EventTemplate) -> None:
        if self.get(event_type):
            SQL('event_templates').update(Record(data=template.data), f"event_type='{event_type}' and guild_id={self.key}")
            self.load()
        else:
            self.add(event_type, template)

    def remove(self, event_type: str) -> None:
        SQL('event_templates').delete(f"guild_id={self.key} and event_type='{event_type}'")
        self.load()