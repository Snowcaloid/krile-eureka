import os
from typing import Union
from discord import Interaction, InteractionResponse


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