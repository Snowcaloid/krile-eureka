

from typing import override
from data_providers.events import EventsProvider
from data_writers._base import BaseWriter
from models.context import ExecutionContext
from models.event import EventStruct


class EventsWriter(BaseWriter[EventStruct]):
    def _validate_input(self, context: ExecutionContext, struct: EventStruct, exists: bool, is_update: bool) -> None:
        if not exists and is_update:
            context.log(f'Event {struct.id} does not exist for update.')
            raise ValueError(f'Event {struct.id} does not exist for update.')
        if exists and not is_update:
            context.log(f'Event {struct.id} already exists for creation.')
            raise ValueError(f'Event {struct.id} already exists for creation.')

    @override
    def sync(self, struct: EventStruct, context: ExecutionContext) -> None:
        with context:
            context.log('Syncing event...')
            found_struct = EventsProvider().find(struct)
            self._validate_input(context, struct, found_struct is not None, False)
            if found_struct:
                context.transaction.sql('events').update(
                    struct.to_record(),
                    where=f'id={struct.id}'
                )
            else:
                context.transaction.sql('events').insert(
                    struct.to_record()
                )
            context.log(f'Successfully synced event {struct}')

    @override
    def remove(self, struct: EventStruct, context: ExecutionContext) -> None:
        with context:
            assert False, 'Events are not removable for archiving purposes.'