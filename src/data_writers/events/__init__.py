

from datetime import datetime
from typing import Optional, override
from data_providers.channel_assignments import ChannelAssignmentProvider
from data_providers.event_templates import EventTemplateProvider
from data_providers.events import EventsProvider
from data_providers.roles import RolesProvider
from data_writers._base import BaseWriter
from models.channel_assignment import ChannelAssignmentStruct
from models.context import ExecutionContext
from models.event import EventStruct
from models.event_template import EventTemplateStruct
from models.permissions import ModulePermissions, PermissionLevel, Permissions
from models.roles import RoleStruct
from utils.basic_types import ChannelFunction, RoleDenominator, RoleFunction
from utils.functions import is_null_or_unassigned


class EventsWriter(BaseWriter[EventStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def _assert_guild_id(self, struct: EventStruct) -> None:
        assert not is_null_or_unassigned(struct.guild_id), \
            'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), \
            f'Invalid guild ID: {struct.guild_id}'

    def _validate_input(self, context: ExecutionContext,
                        struct: EventStruct,
                        old_struct: Optional[EventStruct],
                        deleting: bool) -> None:
        context.assert_permissions(Permissions(modules=ModulePermissions(channels=PermissionLevel.FULL)))
        self._assert_guild_id(struct)
        if deleting:
            assert old_struct, f'struct <{struct}> does not exist and cannot be deleted.'
        if old_struct:
            validating_struct = old_struct.intersect(struct)
        else:
            validating_struct = struct
        assert not is_null_or_unassigned(validating_struct.event_type), 'event type is required.'
        assert not is_null_or_unassigned(validating_struct.timestamp), 'timestamp is required.'
        assert not is_null_or_unassigned(validating_struct.raid_leader), 'raid leader ID is required.'
        event_template = EventTemplateProvider().find(EventTemplateStruct(
            guild_id=validating_struct.guild_id,
            event_type=validating_struct.event_type
        ))
        assert event_template, f'Event template for type {validating_struct.event_type} not found in guild {self._bot.get_guild(validating_struct.guild_id).name}.'
        if not is_null_or_unassigned(validating_struct.timestamp):
            assert validating_struct.timestamp > datetime.utcnow(), \
                f'Timestamp {validating_struct.timestamp} must be in the future.'
        if not is_null_or_unassigned(validating_struct.raid_leader):
            rl = self._bot.get_member(validating_struct.guild_id, validating_struct.raid_leader)
            assert rl, f'Invalid raid leader ID: {validating_struct.raid_leader}'
            role_struct = RolesProvider().find_by_event_template(
                event_template,
                RoleStruct(function=RoleFunction.RAID_LEADER)
            )
            if role_struct:
                assert rl.get_role(role_struct.id), \
                    f'Member {rl.display_name} must have the role {role_struct.role_name} to be able to raid lead.' #type: ignore #TODO: RoleStruct.role_name.
        if not is_null_or_unassigned(validating_struct.custom_description):
            assert len(validating_struct.custom_description) <= 100, 'Custom description must be 100 characters or less.'


    @override
    def sync(self, struct: EventStruct, context: ExecutionContext) -> None:
        with context:
            context.log('syncing event...')
            found_struct = EventsProvider().find(struct)
            self._validate_input(context, struct, found_struct, False)
            if found_struct:
                edited_struct = found_struct.intersect(struct)
                context.transaction.sql('events').update(
                    edited_struct.to_record(),
                    where=f'id={edited_struct.id}'
                )
                context.log(f'Changes: {edited_struct.changes_since(found_struct)}')
            else:
                context.transaction.sql('events').insert(
                    struct.to_record()
                )
            context.log(f'successfully synced event {struct}')

    @override
    def remove(self, struct: EventStruct, context: ExecutionContext) -> None:
        with context:
            assert False, 'Events are not removable for archiving purposes.'