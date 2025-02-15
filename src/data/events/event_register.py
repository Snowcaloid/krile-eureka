
import data.events.event as event


class EventRegister:
    @classmethod
    def register_all(cl) -> None:
        #TODO: Refactor
        # event.EventCategoryCollection.ALL_WITH_CUSTOM = event.Event.all_events_for_category(event.EventCategory.BA) + \
        #     event.Event.all_events_for_category(event.EventCategory.DRS) + \
        #     event.Event.all_events_for_category(event.EventCategory.BOZJA) + \
        #     event.Event.all_events_for_category(event.EventCategory.CHAOTIC) + \
        #     [event.Event]