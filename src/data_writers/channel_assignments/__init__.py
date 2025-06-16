from __future__ import annotations
from typing import override

from data_providers.channel_assignments import ChannelAssignmentProvider
from models.channel_assignment import ChannelAssignmentStruct
from models.context import ExecutionContext
from data_writers._base import BaseWriter

from models.permissions import ModulePermissions, PermissionLevel, Permissions
from utils.basic_types import ChannelDenominator, ChannelFunction
from utils.functions import is_null_or_unassigned

class ChannelAssignmentsWriter(BaseWriter[ChannelAssignmentStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def _assert_guild_id(self, struct: ChannelAssignmentStruct) -> None:
        assert not is_null_or_unassigned(struct.guild_id), \
            'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), \
            f'Invalid guild ID: {struct.guild_id}'

    def _is_value_set_for_denominator(self, struct: ChannelAssignmentStruct) -> bool:
            match struct.denominator:
                case ChannelDenominator.EVENT_TYPE:
                    return not is_null_or_unassigned(struct.event_type)
                case ChannelDenominator.EVENT_CATEGORY:
                    return not is_null_or_unassigned(struct.event_category)
                case ChannelDenominator.NOTORIOUS_MONSTER:
                    return not is_null_or_unassigned(struct.notorious_monster)
                case ChannelDenominator.EUREKA_INSTANCE:
                    return not is_null_or_unassigned(struct.eureka_instance)
            return False

    def _validate_input(self,
                        context: ExecutionContext,
                        struct: ChannelAssignmentStruct,
                        exists: bool,
                        deleting: bool) -> None:
        context.assert_permissions(Permissions(modules=ModulePermissions(channels=PermissionLevel.FULL)))
        self._assert_guild_id(struct)
        if deleting:
            assert exists, f'struct <{struct}> does not exist and cannot be deleted.'
        if not exists:
            assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
            assert not is_null_or_unassigned(struct.function), 'missing function'
        if deleting:
            if is_null_or_unassigned(struct.id):
                context.log('no ID provided, checking for combination of channel ID, function and denominator')
                assert not is_null_or_unassigned(struct.channel_id), 'missing channel ID'
                assert not is_null_or_unassigned(struct.function), 'missing function'
                assert not is_null_or_unassigned(struct.denominator), 'missing denominator'
                assert self._is_value_set_for_denominator(struct), f'missing value for denominator: {struct.denominator.name}'
            assert not is_null_or_unassigned(struct.id) or \
                (not is_null_or_unassigned(struct.channel_id) and \
                 not is_null_or_unassigned(struct.function) and \
                 not is_null_or_unassigned(struct.denominator) and \
                 self._is_value_set_for_denominator(struct)), \
                'missing ID, channel ID, function, denominator or value for denominator'
        if not is_null_or_unassigned(struct.function):
            assert struct.function in ChannelFunction, \
                f'invalid function: {struct.function}'
            assert struct.denominator.is_allowed_function(struct.function), \
                f'invalid denominator: {struct.denominator.name}'
            assert self._is_value_set_for_denominator(struct), \
                f'missing value for denominator: {struct.denominator.name}'
        if not is_null_or_unassigned(struct.channel_id):
            assert self._bot.get_text_channel(struct.channel_id), \
                f'cannot find discord channel with ID: {struct.channel_id}'

    @override
    def sync(self, channel: ChannelAssignmentStruct,
             context: ExecutionContext) -> None:
        with context:
            context.log('syncing channel ...')
            found_channel = ChannelAssignmentProvider().find(channel)
            self._validate_input(context, channel, found_channel is not None, False)
            if found_channel:
                edited_channel = found_channel.intersect(channel)
                context.transaction.sql('channels').update(
                    edited_channel.to_record(),
                    f'id={found_channel.id}')
                context.log(f'Changes: `{edited_channel.changes_since(found_channel)}`')
            else:
                context.transaction.sql('channels').insert(channel.to_record())
            context.log(f'channel assignment synced successfully: `{channel}`')

    @override
    def remove(self, channel: ChannelAssignmentStruct,
               context: ExecutionContext) -> None:
        with context:
            context.log('removing channel ...')
            found_channel = ChannelAssignmentProvider().find(channel)
            self._validate_input(context, channel, found_channel is not None, True)
            context.transaction.sql('channels').delete(found_channel.to_record())
            context.log(f'channel assignment removed successfully: `{channel}`')
