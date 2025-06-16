
from typing import override
from data_providers._base import BaseProvider
from models.event import EventStruct


class EventsProvider(BaseProvider[EventStruct]):
    @override
    def struct_type(self) -> type[EventStruct]:
        return EventStruct