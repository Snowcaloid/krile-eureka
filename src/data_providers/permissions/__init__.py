from os import getenv
from typing import Generator
from discord import Member
from centralized_data import Bindable
from data.events.event_category import EventCategory
from data_providers.roles import RolesProvider
from models.roles import RoleStruct
from models.permissions import (NO_ACCESS, PermissionLevel, ModulePermissions, EventAdministrationPermissions, Permissions, FULL_ACCESS, ADMIN_ACCESS, DEV_ACCESS)
from utils.basic_types import GuildID, ChannelFunction

class PermissionProvider(Bindable):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    def evaluate_permissions_for_user(self, guild_id: GuildID, user_id: int) -> Permissions:
        if guild_id is None or user_id is None: return NO_ACCESS
        user = self.bot._client.get_user(user_id)
        if user is None: return NO_ACCESS
        guild = self.bot._client.get_guild(guild_id)
        if guild is None: return NO_ACCESS
        if self._is_owner(user_id): return FULL_ACCESS
        if self._is_developer(guild_id, user): return DEV_ACCESS
        if self._is_admin(guild_id, user): return ADMIN_ACCESS
        return Permissions(
            modules=self._calculate_module_permissions(guild_id, user),
            event_administration=list(self._calculate_event_administration_permissions(guild_id, user))
        )

    def _is_developer(self, guild_id: GuildID, user: Member) -> bool:
        role = RolesProvider().find(RoleStruct(
            guild_id=guild_id,
            function=ChannelFunction.DEVELOPER
        ))
        return not user.get_role(role.role_id) is None

    def _is_admin(self, guild_id: GuildID, user: Member) -> bool:
        role = RolesProvider().find(RoleStruct(
            guild_id=guild_id,
            function=ChannelFunction.ADMIN
        ))
        return not user.get_role(role.role_id) is None

    def _is_owner(self, user_id: int) -> bool:
        return user_id == int(getenv('OWNER_ID'))

    def _is_raid_leader(self, guild_id: GuildID, user: Member) -> bool:
        for role in RolesProvider().find_all(RoleStruct(
            guild_id=guild_id,
            function=ChannelFunction.RAID_LEADER
        )):
            if user.get_role(role.role_id) is not None:
                return True
        return False

    def _calculate_module_permissions(self, guild_id: GuildID, user: Member) -> ModulePermissions:
        is_raid_leader = self._is_raid_leader(guild_id, user)
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

    def _calculate_event_administration_permissions(self, guild_id: GuildID, user: Member) -> Generator[EventAdministrationPermissions, any, any]:
        is_raid_leader = self._is_raid_leader(guild_id, user)
        for event_category in EventCategory:
            if self._is_raid_leader_for_category(guild_id, user, event_category):
                yield EventAdministrationPermissions(
                        category=event_category,
                        level=PermissionLevel.FULL,
                        event_templates=PermissionLevel.FULL,
                        event_secrets=PermissionLevel.VIEW
                    )
            if is_raid_leader:
                yield EventAdministrationPermissions(
                    category=event_category,
                    level=PermissionLevel.VIEW,
                    event_templates=PermissionLevel.VIEW,
                    event_secrets=PermissionLevel.NONE
                )