from os import getenv
from typing import Any, Generator
from discord import Member
from centralized_data import Bindable
from utils.basic_types import EventCategory, RoleDenominator
from data_providers.role_assignments import RoleAssignmentsProvider
from models.role_assignment import RoleAssignmentStruct
from models.permissions import (NO_ACCESS, PermissionLevel, ModulePermissions, EventAdministrationPermissions, Permissions, FULL_ACCESS, ADMIN_ACCESS, DEV_ACCESS)
from utils.basic_types import GuildID, RoleFunction

class PermissionProvider(Bindable):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    def evaluate_permissions_for_user(self, guild_id: GuildID, user_id: int) -> Permissions:
        if guild_id is None or user_id is None: return NO_ACCESS
        user = self.bot.get_user(user_id)
        if user is None: return NO_ACCESS
        guild = self.bot.get_guild(guild_id)
        if guild is None: return NO_ACCESS
        if self._is_owner(user_id): return FULL_ACCESS
        if self._is_developer(user): return DEV_ACCESS
        if self._is_admin(user): return ADMIN_ACCESS
        return Permissions(
            modules=self._calculate_module_permissions(user),
            event_administration=list(self._calculate_event_administration_permissions(user))
        )

    def _is_developer(self, user: Member) -> bool:
        role = RoleAssignmentsProvider().find(RoleAssignmentStruct(
            guild_id=user.guild.id,
            function=RoleFunction.DEVELOPER
        ))
        return not user.get_role(role.role_id) is None

    def _is_admin(self, user: Member) -> bool:
        role = RoleAssignmentsProvider().find(RoleAssignmentStruct(
            guild_id=user.guild.id,
            function=RoleFunction.ADMIN
        ))
        return not user.get_role(role.role_id) is None

    def _is_owner(self, user_id: int) -> bool:
        owner_id = getenv('BOT_OWNER_ID')
        return owner_id is not None and user_id == int(owner_id)

    def _is_raid_leader(self, user: Member) -> bool:
        for role in RoleAssignmentsProvider().find_all(RoleAssignmentStruct(
            guild_id=user.guild.id,
            function=RoleFunction.RAID_LEADER
        )):
            if user.get_role(role.role_id) is not None:
                return True
        return False

    def _is_raid_leader_for_category(self, user: Member, category: EventCategory) -> bool:
        role_struct = RoleAssignmentsProvider().find(RoleAssignmentStruct(
            guild_id=user.guild.id,
            function=RoleFunction.RAID_LEADER,
            denominator=RoleDenominator.EVENT_CATEGORY,
            event_category=category
        ))
        return role_struct is not None and user.get_role(role_struct.role_id) is not None

    def _calculate_module_permissions(self, user: Member) -> ModulePermissions:
        is_raid_leader = self._is_raid_leader(user)
        return ModulePermissions(
            channels=PermissionLevel.VIEW if is_raid_leader else PermissionLevel.NONE,
            roles=PermissionLevel.VIEW if is_raid_leader else PermissionLevel.NONE,
            messages=PermissionLevel.VIEW if is_raid_leader else PermissionLevel.NONE,
            events=PermissionLevel.FULL if is_raid_leader else PermissionLevel.NONE,
            event_templates=PermissionLevel.FULL if is_raid_leader else PermissionLevel.NONE,
            signups=PermissionLevel.FULL if is_raid_leader else PermissionLevel.NONE,
            faq=PermissionLevel.NONE,
            docs=PermissionLevel.NONE
        )

    def _calculate_event_administration_permissions(self, user: Member) -> Generator[EventAdministrationPermissions, Any, Any]:
        is_raid_leader = self._is_raid_leader(user)
        for event_category in EventCategory:
            if self._is_raid_leader_for_category(user, event_category):
                yield EventAdministrationPermissions(
                        category=event_category,
                        level=PermissionLevel.FULL,
                        event_templates=PermissionLevel.FULL,
                        event_secrets=PermissionLevel.VIEW
                    )
            elif is_raid_leader:
                yield EventAdministrationPermissions(
                    category=event_category,
                    level=PermissionLevel.VIEW,
                    event_templates=PermissionLevel.VIEW,
                    event_secrets=PermissionLevel.NONE
                )