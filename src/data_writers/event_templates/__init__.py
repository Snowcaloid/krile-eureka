
from typing import override

from utils.basic_types import EventCategory
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
        assert not is_null_or_unassigned(struct.guild_id), 'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), f'Invalid guild ID: {struct.guild_id}'

    def _validate_data(self, struct: EventTemplateStruct) -> None:
        assert struct.data.type == struct.event_type, \
            f'struct data type {struct.data.type} does not match struct event type {struct.event_type}'
        assert struct.data.description, \
            'missing description in event template data'
        assert struct.data.short_description, \
            'missing short description in event template data'
        assert struct.data.category in EventCategory.__members__, \
            f'invalid category {struct.data.category} in event template data, must be one of {list(EventCategory.__members__.values())}'
        value = struct.data.source.get('recruitment_post_title')
        assert value, 'missing recruitment post title in event template data'
        assert '%description' in value, \
            'recruitment post title must contain %description placeholder'
        value = struct.data.source.get('party_descriptions')
        assert value, 'missing party descriptions in event template data'
        value = struct.data.source.get('schedule_entry_text')
        assert value, 'missing schedule entry text in event template data'
        assert value.startswith('(%time ST (%localtime LT)): '), \
            'schedule entry text must start with "(%time ST (%localtime LT)): "'
        assert '%rl' in value, 'raid leader placeholder %rl missing in schedule entry text'
        if struct.data.use_passcodes:
            value = struct.data.source.get('passcode_post_title')
            assert value, 'missing passcode post title in event template data'
            value = struct.data.source.get('main_passcode_text')
            assert value, 'missing main passcode text in event template data'
            assert '%passcode' in value, \
                'main passcode text must contain %passcode placeholder'
            assert struct.data.source.get('dm_title'), \
                'missing DM title in event template data'
            value = struct.data.source.get('party_leader_dm_text')
            assert value, 'missing party leader DM text in event template data'
            assert '%passcode' in value, \
                'party leader DM text must contain %passcode placeholder'
            assert '%party' in value, \
                'party leader DM text must contain %party placeholder'
            value = struct.data.source.get('raid_leader_dm_text')
            assert value, 'missing raid leader DM text in event template data'
            assert '%passcode_main' in value, \
                'raid leader DM text must contain %passcode_main placeholder'
            assert struct.data.pl_passcode_delay is not None, \
            'missing PL passcode delay in event template data'
            if struct.data.use_support:
                value = struct.data.source.get('support_passcode_text')
                assert value, 'missing support passcode text in event template data'
                assert '%passcode' in value, \
                    'support passcode text must contain %passcode placeholder'
                value = struct.data.source.get('support_party_leader_dm_text')
                assert value, 'missing support party leader DM text in event template data'
                assert '%passcode' in value, \
                    'support party leader DM text must contain %passcode placeholder'
                assert '%passcode_support' in struct.data.source['raid_leader_dm_text'], \
                    'raid leader DM text must contain %passcode_support placeholder'
                assert struct.data.support_passcode_delay is not None, \
                    'missing support passcode delay in event template data'

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
        self._validate_data(struct)

    @override
    def sync(self, struct: EventTemplateStruct, context: ExecutionContext) -> None:
        with context:
            found_struct = EventTemplateProvider().find(struct)
            self._validate_input(context, struct, found_struct is not None, False)
            context.log('Syncing event template...')
            if found_struct:
                context.transaction.sql('event_templates').update(
                    struct.to_record(),
                    where=f'guild_id={struct.guild_id} and event_type=\'{struct.event_type}\''
                )
            else:
                context.transaction.sql('event_templates').insert(struct.to_record())
            context.log(f'Event type {struct.event_type} synced successfully.')

    @override
    def remove(self, struct: EventTemplateStruct, context: ExecutionContext) -> None:
        with context:
            context.log('Removing event template...')
            found_struct = EventTemplateProvider().find(struct)
            self._validate_input(context, struct, found_struct is not None, True)
            context.transaction.sql('event_templates').delete(struct.to_record())
            context.log(f'Event type {struct.event_type} removed successfully.')