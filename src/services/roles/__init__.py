from __future__ import annotations
from typing import override
from data.db.sql import SQL
from data.events.event_category import EventCategory
from data.events.event_templates import EventTemplates
from services._base import BaseGuildService
from providers.roles import RolesProvider
from models.roles import RoleStruct
from models.context import ExecutionContext
from models.permissions import ModulePermissions, PermissionLevel, Permissions

class RolesService(BaseGuildService[RoleStruct]):
    from services.roles.user_input import RoleUserInput
    @RoleUserInput.bind
    def _user_input(self) -> RoleUserInput: ...

    @override
    def sync(self, role: RoleStruct, context: ExecutionContext) -> None:
        with context:
            context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
            assert role.guild_id is not None, "Role sync failure: RoleStruct is missing Guild ID"
            found_role = RolesProvider().find(role)
            if found_role:
                edited_role = found_role.intersect(role)
                SQL('roles').update(
                    edited_role.to_record(),
                    f'id={found_role.id}')
                context.log(f"[ROLES] #{edited_role} updated successfully.")
            elif self._user_input.can_insert(role):
                SQL('roles').insert(role.to_record())
                context.log(f"[ROLES] #{role} added successfully.")
            self.load()

    def sync_category(self, channel: RoleStruct, event_category: EventCategory, context: ExecutionContext) -> None:
        with context:
            for event_template in EventTemplates(self.key).get_by_categories([event_category]):
                self.sync(channel.intersect(RoleStruct(event_category=event_template.type())), context)

    @override
    def remove(self, role: RoleStruct, context: ExecutionContext) -> None:
        with context:
            context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
            assert role.guild_id is not None, "Role removal failure: RoleStruct is missing Guild ID"
            found_role = RolesProvider().find(role)
            if found_role:
                SQL('roles').delete(f'id={found_role.id}')
                context.log(f"[ROLES] #{found_role} removed successfully.")
            elif self._user_input.can_remove(role):
                event_type_part = f"and event_type='{role.event_category}'" if role.event_category else ''
                SQL('roles').delete((
                    f'guild_id={role.guild_id} and channel_id={role.role_id} '
                    f'and function={role.function.value} {event_type_part}'))
                context.log(f"[ROLES] #{role} removed successfully.")
            self.load()