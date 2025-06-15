
from typing import override

from data_providers.event_templates import EventTemplateProvider
from data_writers._base import BaseWriter
from models.context import ExecutionContext
from models.event_template import EventTemplateStruct
from models.permissions import ModulePermissions, PermissionLevel, Permissions
from utils.functions import is_null_or_unassigned


class EventTemplatesWriter(BaseWriter[EventTemplateStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def _assert_guild_id(self, struct: EventTemplateStruct) -> None:
        assert not is_null_or_unassigned(struct.guild_id), \
            'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), \
            f'Invalid guild ID: {struct.guild_id}'

    def _validate_input(self,
                        context: ExecutionContext,
                        struct: EventTemplateStruct,
                        exists: bool,
                        deleting: bool) -> None:
        context.assert_permissions(Permissions(modules=ModulePermissions(event_templates=PermissionLevel.FULL)))
        self._assert_guild_id(struct)
        if deleting:
            assert exists, f'struct <{struct}> does not exist and cannot be deleted.'
        if not exists:
            assert not is_null_or_unassigned(struct.event_type), 'missing event type'
            assert not is_null_or_unassigned(struct.data), 'missing data'
            assert EventTemplateProvider().find(EventTemplateStruct(guild_id=struct.guild_id, event_type=struct.event_type)) is None, \
                f'event template for type {struct.event_type} already exists in guild {struct.guild_id}.'


    @override
    def sync(self, struct: EventTemplateStruct, context: ExecutionContext) -> None:
        with context:
            found_struct = EventTemplateProvider().find(struct)
            self._validate_input(context, struct, found_struct is not None, False)
            context.log('Syncing event template...')

            context.log(f'Event type {struct.event_type} synced successfully.')

    @override
    def remove(self, struct: EventTemplateStruct, context: ExecutionContext) -> None:
        ...