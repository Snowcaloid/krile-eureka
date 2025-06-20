from typing import Type, override
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

    @override
    def provider(self) -> ButtonsProvider: return ButtonsProvider()

    @override
    def _validate_input(self, context: ExecutionContext,
                        struct: ButtonStruct,
                        old_struct: ButtonStruct | None,
                        deleting: bool) -> None:
        if deleting:
            assert old_struct, f'cannot delete button {struct} that does not exist.'
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
