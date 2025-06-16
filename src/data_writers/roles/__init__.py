from __future__ import annotations
from typing import override
from data_providers.roles import RolesProvider
from models.roles import RoleStruct
from models.context import ExecutionContext
from models.permissions import ModulePermissions, PermissionLevel, Permissions
from data_writers._base import BaseWriter

class RolesWriter(BaseWriter[RoleStruct]):

    def _can_insert(self, struct: RoleStruct) -> bool:
        assert struct.role_id is not None, "Role sync insert failure: RoleStruct is missing Role ID"
        assert struct.function is not None, "Role sync insert failure: RoleStruct is missing function"
        return True

    def _can_remove(self, struct: RoleStruct) -> bool:
        assert struct.role_id is not None, "Role removal failure: RoleStruct is missing Role ID"
        assert struct.function is not None, "Role removal failure: RoleStruct is missing function"
        return True

    @override
    def sync(self, role: RoleStruct, context: ExecutionContext) -> None:
        with context:
            context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
            assert role.guild_id is not None, "Role sync failure: RoleStruct is missing Guild ID"
            found_role = RolesProvider().find(role)
            if found_role:
                edited_role = found_role.intersect(role)
                context.transaction.sql('roles').update(
                    edited_role.to_record(),
                    f'id={found_role.id}')
                context.log(f"[ROLES] #{edited_role} updated successfully.")
            elif self._can_insert(role):
                context.transaction.sql('roles').insert(role.to_record())
                context.log(f"[ROLES] #{role} added successfully.")

    # def sync_category(self, channel: RoleStruct, event_category: EventCategory, context: ExecutionContext) -> None:
    #     with context:
    #         for event_template in EventTemplates(self.key).get_by_categories([event_category]):
    #             self.sync(channel.intersect(RoleStruct(event_category=event_template.type())), context)

    @override
    def remove(self, role: RoleStruct, context: ExecutionContext) -> None:
        with context:
            context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
            assert role.guild_id is not None, "Role removal failure: RoleStruct is missing Guild ID"
            found_role = RolesProvider().find(role)
            if found_role:
                context.transaction.sql('roles').delete(f'id={found_role.id}')
                context.log(f"[ROLES] #{found_role} removed successfully.")
            elif self._can_remove(role):
                event_type_part = f"and event_type='{role.event_category}'" if role.event_category else ''
                context.transaction.sql('roles').delete((
                    f'guild_id={role.guild_id} and channel_id={role.role_id} '
                    f'and function={role.function.value} {event_type_part}'))
                context.log(f"[ROLES] #{role} removed successfully.")