
from centralized_data import GlobalCollection
from data.events.event_category import EventCategory
from utils.basic_types import GuildID


class EventTypesService(GlobalCollection[GuildID]):
    # Event types
    def is_event_type(self, event_type: str) -> bool:
        """Check if the given event type is valid."""
        from data.events.event_templates import EventTemplates
        return event_type in [event_template.type() for event_template in EventTemplates(self.key).all]

    def event_type_name_to_type(self, event_type: str) -> str:
        from data.events.event_templates import EventTemplates
        for event in EventTemplates(self.key).all:
            if event.description() == event_type:
                return event.type()
        return event_type

    # Event categories
    def is_event_category(self, event_type: str) -> bool:
        """Check if the given event type is a valid event category."""
        return event_type.replace('_CATEGORY', '') in EventCategory._value2member_map_

    def event_category_name_to_category(self, event_category_name: str) -> EventCategory:
        for choice in EventCategory.all_category_choices():
            if choice.name == event_category_name:
                return choice.value
        return EventCategory(event_category_name)