

from typing import override

from data_providers.message_assignments import MessageAssignmentsProvider
from data_writers._base import BaseWriter
from models.context import ExecutionContext
from models.message_assignment import MessageAssignmentStruct
from models.permissions import ModulePermissions, PermissionLevel, Permissions
from utils.functions import is_null_or_unassigned


class MessageAssignmentsWriter(BaseWriter[MessageAssignmentStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def provider(self) -> MessageAssignmentsProvider: return MessageAssignmentsProvider()

    def _assert_guild_id(self, struct: MessageAssignmentStruct) -> None:
        assert not is_null_or_unassigned(struct.guild_id), \
            'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), \
            f'Invalid guild ID: {struct.guild_id}'

    @override
    def _validate_input(self, context: ExecutionContext,
                        struct: MessageAssignmentStruct,
                        old_struct: MessageAssignmentStruct | None,
                        deleting: bool) -> None:
        context.assert_permissions(Permissions(modules=ModulePermissions(messages=PermissionLevel.FULL)))
        self._assert_guild_id(struct)
        if deleting:
            assert old_struct, f'struct <{struct}> does not exist and cannot be deleted.'
            if is_null_or_unassigned(struct.id):
                context.log('no ID provided, checking for combination of channel ID, message ID and function')
                assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
                assert not is_null_or_unassigned(struct.message_id), 'missing message ID'
                assert not is_null_or_unassigned(struct.function), 'missing function'
        if not old_struct:
            assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
            assert not is_null_or_unassigned(struct.message_id), 'missing message ID'
            assert not is_null_or_unassigned(struct.function), 'missing function'
