

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

    def _assert_guild_id(self, struct: MessageAssignmentStruct) -> None:
        assert not is_null_or_unassigned(struct.guild_id), \
            'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), \
            f'Invalid guild ID: {struct.guild_id}'

    def _validate_input(self,
                        context: ExecutionContext,
                        struct: MessageAssignmentStruct,
                        exists: bool,
                        deleting: bool) -> None:
        context.assert_permissions(Permissions(modules=ModulePermissions(messages=PermissionLevel.FULL)))
        self._assert_guild_id(struct)
        if deleting:
            assert exists, f'struct <{struct}> does not exist and cannot be deleted.'
            if is_null_or_unassigned(struct.id):
                context.log('no ID provided, checking for combination of channel ID, message ID and function')
                assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
                assert not is_null_or_unassigned(struct.message_id), 'missing message ID'
                assert not is_null_or_unassigned(struct.function), 'missing function'
        if not exists:
            assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
            assert not is_null_or_unassigned(struct.message_id), 'missing message ID'
            assert not is_null_or_unassigned(struct.function), 'missing function'

    @override
    def sync(self, struct: MessageAssignmentStruct, context: ExecutionContext) -> None:
        with context:
            context.log('syncing message assignment...')
            found_struct = MessageAssignmentsProvider().find(struct)
            self._validate_input(context, struct, found_struct is not None, False)
            if found_struct:
                context.transaction.sql('message_assignments').update(
                    record=struct.to_record(),
                    where=f"id = {found_struct.id}"
                )
                context.log(f'changes: {struct.changes_since(found_struct)}')
            else:
                context.transaction.sql('message_assignments').insert(
                    record=struct.to_record()
                )
                context.log(f'message assignment created: {struct}')
            context.log(f'message assignment successfully synced.')

    @override
    def remove(self, struct: MessageAssignmentStruct, context: ExecutionContext) -> None:
        with context:
            context.log('removing message assignment...')
            found_struct = MessageAssignmentsProvider().find(struct)
            self._validate_input(context, struct, found_struct is not None, True)
            context.transaction.sql('message_assignments').delete(found_struct.to_record())
            context.log(f'message assignment removed: {struct}')
