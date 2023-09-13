import os
from typing import Tuple, Union
from discord import Interaction, InteractionResponse, Member
import bot
from data.guilds.guild_role_functions import GuildRoleFunction


class PermissionValidator:
    @classmethod
    def is_developer(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        rolename = os.getenv('ROLE_DEVELOPER').lower()
        for role in interaction.user.roles:
            if rolename in role.name.lower():
                return True
        return False

    @classmethod
    def is_admin(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        for role in interaction.user.roles:
            if role.permissions.administrator or role.name.lower() == os.getenv('ROLE_ADMIN').lower():
                return True
        return self.is_developer(interaction)

    @classmethod
    def is_raid_leader(self, interaction: Union[Interaction, InteractionResponse]) -> bool:
        for role in interaction.user.roles:
            if 'raid lead' in role.name.lower():
                return True
        return self.is_admin(interaction)

    @classmethod
    def get_raid_leader_permissions(self, member: Member) -> Tuple[bool, bool, bool]:
        allow_ba = False
        allow_drs = False
        allow_bozja = False
        for role in member.roles:
            if role.permissions.administrator or role.name.lower() == os.getenv('ROLE_ADMIN').lower():
                return True, True, True
            elif 'ba raid lead' in role.name.lower():
                allow_ba = True
            elif 'drs raid lead' in role.name.lower():
                allow_drs = True
            elif 'castrum raid lead' in role.name.lower() or 'drn run leader' in role.name.lower():
                allow_bozja = True
        return allow_ba, allow_drs, allow_bozja

    @classmethod
    def allowed_to_react_to_missed_post(self, member: Member, event_category: str) -> bool:
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