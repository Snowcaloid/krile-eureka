
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