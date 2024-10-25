import os
from typing import Tuple, Union
from discord import Interaction, InteractionResponse, Member
import bot
from data.events.event import EventCategory
from data.guilds.guild_role_functions import GuildRoleFunction


class PermissionValidator:
    @classmethod
    def is_in_guild(cl, interaction: Union[Interaction, InteractionResponse]) -> bool:
        return not interaction.guild is None

    @classmethod
    def is_owner(cl, interaction: Union[Interaction, InteractionResponse]) -> bool:
        return interaction.user.id == int(os.getenv('OWNER_ID'))

    @classmethod
    def is_developer(cl, interaction: Union[Interaction, InteractionResponse]) -> bool:
        if cl.is_in_guild(interaction):
            role_id = bot.instance.data.guilds.get(interaction.guild_id).role_developer
            if not role_id: return cl.is_owner(interaction)
            return not interaction.user.get_role(role_id) is None or cl.is_owner(interaction)
        return False

    @classmethod
    def is_admin(cl, interaction: Union[Interaction, InteractionResponse]) -> bool:
        if cl.is_in_guild(interaction):
            role_id = bot.instance.data.guilds.get(interaction.guild_id).role_admin
            if not role_id: return cl.is_developer(interaction)
            return not interaction.user.get_role(role_id) is None or cl.is_developer(interaction)
        return False

    @classmethod
    def is_raid_leader(cl, interaction: Union[Interaction, InteractionResponse]) -> bool:
        if cl.is_in_guild(interaction):
            raid_leader_roles = bot.instance.data.guilds.get(interaction.guild_id).roles.get(GuildRoleFunction.RAID_LEADER)
            for role in raid_leader_roles:
                if not interaction.user.get_role(role.role_id) is None:
                    return True
            return cl.is_admin(interaction)
        return False

    @classmethod
    def get_raid_leader_permissions(cl, member: Member) -> Tuple[bool, bool, bool]:
        guild_roles = bot.instance.data.guilds.get(member.guild.id).roles
        admin_role_id = bot.instance.data.guilds.get(member.guild.id).role_admin
        allow_ba = False
        allow_drs = False
        allow_bozja = False
        for role in member.roles:
            if role.id == admin_role_id:
                return True, True, True
            elif [True for guild_role in guild_roles.get(GuildRoleFunction.RAID_LEADER, EventCategory.BA.value) if guild_role.role_id == role.id]:
                allow_ba = True
            elif [True for guild_role in guild_roles.get(GuildRoleFunction.RAID_LEADER, EventCategory.DRS.value) if guild_role.role_id == role.id]:
                allow_drs = True
            elif [True for guild_role in guild_roles.get(GuildRoleFunction.RAID_LEADER, EventCategory.BOZJA.value) if guild_role.role_id == role.id]:
                allow_bozja = True
        return allow_ba, allow_drs, allow_bozja

    @classmethod
    def allowed_to_react_to_missed_post(cl, member: Member, event_category: str) -> bool:
        guild_roles = bot.instance.data.guilds.get(member.guild.id).roles
        allowed_roles = guild_roles.get(GuildRoleFunction.ALLOW_MISSED_RUN_APPLICATION, event_category)
        forbidden_roles = guild_roles.get(GuildRoleFunction.FORBID_MISSED_RUN_APPLICATION, event_category)
        result = False
        for role in member.roles:
            for role_data in forbidden_roles:
                if role.id == role_data.role_id:
                    return False
            for role_data in allowed_roles:
                if role.id == role_data.role_id:
                    result = True
        return result