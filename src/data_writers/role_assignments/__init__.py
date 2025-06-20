from __future__ import annotations
from typing import override
from data_providers.role_assignments import RoleAssignmentsProvider
from models.role_assignment import RoleAssignmentStruct
from models.context import ExecutionContext
from models.permissions import ModulePermissions, PermissionLevel, Permissions
from data_writers._base import BaseWriter
from utils.basic_types import RoleDenominator, RoleFunction
from utils.functions import is_null_or_unassigned

class RoleAssignmentsWriter(BaseWriter[RoleAssignmentStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def _assert_guild_id(self, struct: RoleAssignmentStruct) -> None:
        assert not is_null_or_unassigned(struct.guild_id), \
            'missing Guild ID'
        assert self._bot.get_guild(struct.guild_id), \
            f'Invalid guild ID: {struct.guild_id}'


    def _is_value_set_for_denominator(self, struct: RoleAssignmentStruct) -> bool:
            match struct.denominator:
                case RoleDenominator.EVENT_TYPE:
                    return not is_null_or_unassigned(struct.event_type)
                case RoleDenominator.EVENT_CATEGORY:
                    return not is_null_or_unassigned(struct.event_category)
                case RoleDenominator.NOTORIOUS_MONSTER:
                    return not is_null_or_unassigned(struct.notorious_monster)
                case RoleDenominator.EUREKA_INSTANCE:
                    return not is_null_or_unassigned(struct.eureka_instance)
            return False


    def _validate_input(self,
                        context: ExecutionContext,
                        struct: RoleAssignmentStruct,
                        exists: bool,
                        deleting: bool) -> None:
        context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
        self._assert_guild_id(struct)
        if deleting:
            assert exists, f"Role {struct} does not exist in the database."
        if not exists:
            assert not is_null_or_unassigned(struct.role_id), 'missing role ID'
            assert not is_null_or_unassigned(struct.function), 'missing function'
        if deleting:
            if is_null_or_unassigned(struct.id):
                context.log('no ID provided, checking for combination of role ID, function and denominator')
                assert not is_null_or_unassigned(struct.role_id), 'missing role ID'
                assert not is_null_or_unassigned(struct.function), 'missing function'
                assert not is_null_or_unassigned(struct.denominator), 'missing denominator'
                assert self._is_value_set_for_denominator(struct), f'missing value for denominator: {struct.denominator.name}'
            assert not is_null_or_unassigned(struct.id) or \
                (not is_null_or_unassigned(struct.role_id) and \
                 not is_null_or_unassigned(struct.function) and \
                 not is_null_or_unassigned(struct.denominator) and \
                 self._is_value_set_for_denominator(struct)), \
                'missing ID, role ID, function, denominator or value for denominator'
        if not is_null_or_unassigned(struct.function):
            assert struct.function in RoleFunction, \
                f'invalid function: {struct.function}'
            assert struct.denominator.is_allowed_function(struct.function), \
                f'invalid denominator: {struct.denominator.name}'
            assert self._is_value_set_for_denominator(struct), \
                f'missing value for denominator: {struct.denominator.name}'
        if not is_null_or_unassigned(struct.role_id):
            assert self._bot.get_text_channel(struct.role_id), \
                f'cannot find discord role with ID: {struct.role_id}'

    @override
    def sync(self, role: RoleAssignmentStruct, context: ExecutionContext) -> None:
        with context:
            context.log('syncing role ...')
            found_role = RoleAssignmentsProvider().find(role)
            self._validate_input(context, role, found_role is not None, False)
            if found_role:
                edited_role = found_role.intersect(role)
                context.transaction.sql('role_assignments').update(
                    edited_role.to_record(),
                    f'id={found_role.id}')
                context.log(f'Changes: `{edited_role.changes_since(found_role)}`')
            else:
                context.transaction.sql('role_assignments').insert(role.to_record())
            context.log(f'role assignment synced successfully: `{role}`')

    @override
    def remove(self, role: RoleAssignmentStruct, context: ExecutionContext) -> None:
        with context:
            context.log('removing role ...')
            found_role = RoleAssignmentsProvider().find(role)
            self._validate_input(context, role, found_role is not None, True)
            context.transaction.sql('role_assignments').delete(found_role.to_record())
            context.log(f'role assignment removed successfully: `{role}`')