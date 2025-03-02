from __future__ import annotations
import os
from discord.ext.commands import Bot
from typing import List, Union
from centralized_data import Bindable, Singleton
from discord import Interaction, InteractionResponse, Member
from data.events.event_category import EventCategory
from basic_types import GuildRoleFunction
from data.guilds.guild_roles import GuildRoles

class FakeInteraction:
    def __init__(self, user_id: int, guild_id: int) -> None:
        client: Bot = Singleton.get_instance(Bot)
        self.guild = client.get_guild(guild_id)
        self.guild_id = guild_id
        if self.guild is None: return
        self.user = self.guild.get_member(user_id)

InteractionLike = Union[Interaction, InteractionResponse, FakeInteraction]

class PermissionValidator(Bindable):
    def is_in_guild(self, interaction: InteractionLike) -> bool:
        return not interaction.guild is None

    def is_owner(self, interaction: InteractionLike) -> bool:
        return interaction.user.id == int(os.getenv('OWNER_ID'))

    def is_developer(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_id = GuildRoles(interaction.guild_id).get(GuildRoleFunction.DEVELOPER)
            if not role_id: return self.is_owner(interaction)
            return not interaction.user.get_role(role_id) is None or self.is_owner(interaction)
        return False

    def is_admin(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_id = GuildRoles(interaction.guild_id).get(GuildRoleFunction.ADMIN)
            if not role_id: return self.is_developer(interaction)
            return not interaction.user.get_role(role_id) is None or self.is_developer(interaction)
        return False

    def is_raid_leader(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            raid_leader_roles = GuildRoles(interaction.guild_id).get(GuildRoleFunction.RAID_LEADER)
            for role in raid_leader_roles:
                if not interaction.user.get_role(role.role_id) is None:
                    return True
            return self.is_admin(interaction)
        return False

    def get_raid_leader_permissions(self, member: Member) -> List[EventCategory]:
        guild_roles = GuildRoles(member.guild.id)
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
