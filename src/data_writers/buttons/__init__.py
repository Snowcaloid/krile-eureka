from typing import override
from data_providers.events import EventsProvider
from models.button import ButtonStruct
from models.context import ExecutionContext
from data_providers.buttons import ButtonsProvider
from data_writers._base import BaseWriter
from models.event import EventStruct
from utils.functions import is_null_or_unassigned
from utils.basic_types import ButtonType

class ButtonsWriter(BaseWriter[ButtonStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def _validate_input(self, struct: ButtonStruct,
                        context: ExecutionContext,
                        exists: bool,
                        deleting: bool) -> None:
        if deleting:
            assert exists, f'cannot delete button {struct} that does not exist.'
        assert not is_null_or_unassigned(struct.button_id), 'missing button ID'
        assert not is_null_or_unassigned(struct.label), 'missing button label'
        assert not is_null_or_unassigned(struct.button_type), 'missing button type'
        assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
        assert self._bot.get_text_channel(struct.channel_id), \
            f'channel {struct.channel_id} not found'
        assert not is_null_or_unassigned(struct.message_id), 'missing message ID'
        assert not is_null_or_unassigned(struct.row), 'missing row number'
        assert not is_null_or_unassigned(struct.index), 'missing row index'
        match struct.button_type:
            case ButtonType.ROLE_SELECTION:
                assert not is_null_or_unassigned(struct.role_id), 'missing role ID for role selection button'
            case ButtonType.RECRUITMENT:
                assert not is_null_or_unassigned(struct.party), 'missing party for recruitment button'
                assert struct.party <= 0 or struct.party >= 8, 'party number must be between 1 and 7'
                assert not is_null_or_unassigned(struct.role_id), 'missing role for recruitment button'
                assert self._bot.get_role(context.guild_id, struct.role_id), \
                    f'role {struct.role_id} not found for recruitment button'
                assert not is_null_or_unassigned(struct.event_id), 'missing event ID for recruitment button'
                event_struct = EventsProvider().find(EventStruct(guild_id=context.guild_id, id=struct.event_id))
                assert event_struct, f'event #{struct.event_id} not found for recruitment button'

    @override
    def sync(self, struct: ButtonStruct, context: ExecutionContext) -> None:
        with context:
            found_struct = ButtonsProvider().find(struct)
            self._validate_input(struct, context, found_struct is not None, False)
            if found_struct:
                edited_struct = found_struct.intersect(struct)
                context.transaction.sql('buttons').update(
                    edited_struct.to_record(),
                    f'id={found_struct.button_id}')
                context.log(f'Changes: ```{edited_struct.changes_since(found_struct)}```')
            else:
                context.transaction.sql('buttons').insert(struct.to_record())
            context.log(f'successfully synced button {struct}.')

    @override
    def remove(self, struct: ButtonStruct, context: ExecutionContext) -> None:
        with context:
            found_struct = ButtonsProvider().find(struct)
            self._validate_input(struct, context, found_struct is not None, True)
            context.transaction.sql('buttons').delete(f'button_id={found_struct.button_id}')
            context.log(f'successfully removed button {struct}.')