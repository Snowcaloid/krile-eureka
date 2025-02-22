from __future__ import annotations
import os
from typing import List, Union
from centralized_data import Bindable
from discord import Interaction, InteractionResponse, Member
from data.events.event_category import EventCategory
from basic_types import GuildRoleFunction


class PermissionValidator(Bindable):
    from data.guilds.guild import Guilds
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    def is_in_guild(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        return not interaction.guild is None

    def is_owner(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        return interaction.user.id == int(os.getenv('OWNER_ID'))

    def is_developer(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        if self.is_in_guild(interaction):
            role_id = self.guilds.get(interaction.guild_id).role_developer
            if not role_id: return self.is_owner(interaction)
            return not interaction.user.get_role(role_id) is None or self.is_owner(interaction)
        return False

    def is_admin(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        if self.is_in_guild(interaction):
            role_id = self.guilds.get(interaction.guild_id).role_admin
            if not role_id: return self.is_developer(interaction)
            return not interaction.user.get_role(role_id) is None or self.is_developer(interaction)
        return False

    def is_raid_leader(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        if self.is_in_guild(interaction):
            raid_leader_roles = self.guilds.get(interaction.guild_id).roles.get(GuildRoleFunction.RAID_LEADER)
            for role in raid_leader_roles:
                if not interaction.user.get_role(role.role_id) is None:
                    return True
            return self.is_admin(interaction)
        return False

    def get_raid_leader_permissions(self, member: Member) -> List[EventCategory]:
        guild_roles = self.guilds.get(member.guild.id).roles
        admin_role_id = self.guilds.get(member.guild.id).role_admin
        categories: List[EventCategory] = []
        for role in member.roles:
            if role.id == admin_role_id:
                return list(EventCategory)
            else:
                for guild_role in guild_roles.get_by_id(role.id):
                    if guild_role.function == GuildRoleFunction.RAID_LEADER and not guild_role.event_category in categories:
                        categories.append(EventCategory(guild_role.event_category))
        return categories
