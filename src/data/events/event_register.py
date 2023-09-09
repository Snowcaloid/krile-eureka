
import data.events.event as event
import data.events.ba_events as ba_events
import data.events.drs_events as drs_events
import data.events.bozja_events as bozja_events


class EventRegister:
    @classmethod
    def register_all(cl) -> None:
        event.Event.register()
        ba_events.BA_Normal.register()
        ba_events.BA_Reclear.register()
        ba_events.BA_Collab.register()
        ba_events.BA_Special.register()
        drs_events.DRS_Normal.register()
        drs_events.DRS_Reclear.register()
        bozja_events.DRN_Newbie.register()
        bozja_events.DRN_Reclear.register()
        bozja_events.Castrum.register()
        bozja_events.Dalriada.register()
        bozja_events.CastrumAndDalriada.register()
        bozja_events.BozjaAllRounder.register()
        event.EventCategoryCollection.ALL_WITH_CUSTOM = event.Event.all_events_for_category(event.EventCategory.BA) + \
            event.Event.all_events_for_category(event.EventCategory.DRS) + \
            event.Event.all_events_for_category(event.EventCategory.BOZJA) + \
            [event.Event]