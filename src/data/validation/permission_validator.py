from __future__ import annotations
import os
from typing import List
from centralized_data import Bindable
from discord import Member
from models.roles import RoleStruct
from providers.roles import RolesProvider
from utils.discord_types import InteractionLike
from data.events.event_category import EventCategory
from utils.basic_types import GuildRoleFunction
from utils.functions import is_null_or_unassigned

class PermissionValidator(Bindable):
    def is_in_guild(self, interaction: InteractionLike) -> bool:
        return not interaction.guild is None

    def is_owner(self, interaction: InteractionLike) -> bool:
        return interaction.user.id == int(os.getenv('OWNER_ID'))

    def is_developer(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_struct = RolesProvider(interaction.guild_id).find(RoleStruct(
                function=GuildRoleFunction.DEVELOPER
            ))
            if is_null_or_unassigned(role_struct.role_id): return self.is_owner(interaction)
            return not interaction.user.get_role(role_struct.role_id) is None or self.is_owner(interaction)
        return False

    def is_admin(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_struct = RolesProvider(interaction.guild_id).find(RoleStruct(
                function=GuildRoleFunction.ADMIN
            ))
            if is_null_or_unassigned(role_struct.role_id): return self.is_developer(interaction)
            return not interaction.user.get_role(role_struct.role_id) is None or self.is_developer(interaction)
        return False

    def is_raid_leader(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_structs = RolesProvider(interaction.guild_id).find_all(RoleStruct(
                function=GuildRoleFunction.RAID_LEADER
            ))
            for role_struct in role_structs:
                if not interaction.user.get_role(role_struct.role_id) is None:
                    return True
            return self.is_admin(interaction)
        return False

    def get_raid_leader_permissions(self, member: Member) -> List[EventCategory]:
        admin_role_id = guild_roles.get(GuildRoleFunction.ADMIN)
        categories: List[EventCategory] = []
        for role in member.roles:
            if role.id == admin_role_id:
                return list(EventCategory)
            else:
                for guild_role in guild_roles.get_by_id(role.id):
                    if guild_role.function == GuildRoleFunction.RAID_LEADER and not guild_role.event_category in categories:
                        categories.append(EventCategory(guild_role.event_category))
        return categories
