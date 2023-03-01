import os
from typing import Tuple, Union
from discord import Interaction, InteractionResponse, Member


def permission_developer(interaction: Union[Interaction, InteractionResponse]) -> bool:
    rolename = os.getenv('ROLE_DEVELOPER').lower()
    for role in interaction.user.roles:
        if rolename in role.name.lower():
            return True
    return False

def permission_admin(interaction: Union[Interaction, InteractionResponse]) -> bool:
    for role in interaction.user.roles:
        if role.permissions.administrator:
            return True
    return permission_developer(interaction)

def permission_raid_leader(interaction: Union[Interaction, InteractionResponse]) -> bool:
    for role in interaction.user.roles:
        if 'raid leader' in role.name.lower():
            return True
    return permission_admin(interaction)

def get_raid_leader_permissions(member: Member) -> Tuple[bool, bool]:
    return True, True # remove this if you want specific setting based on roles
    allow_ba = False
    allow_drs = False
    for role in member.roles:
        if role.permissions.administrator:
            return True, True
        elif 'ba raid lead' in role.name.lower():
            allow_ba = True
        elif 'drs raid lead' in role.name.lower():
            allow_drs = True
    return allow_ba, allow_drs