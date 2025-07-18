from models.button.discord_button import DiscordButton
from models.button.button_template import ButtonTemplate
from utils.basic_types import ButtonType
from utils.functions import default_defer

from discord import Embed, Interaction, Role

from typing import List

class RoleDisplayButton(ButtonTemplate):
    """Buttons, which display roles to the person who clicks them"""

    def button_type(self) -> ButtonType: return ButtonType.ROLE_DISPLAY

    async def callback(self, interaction: Interaction, button: DiscordButton):
        await default_defer(interaction)
        roles: List[Role] = interaction.user.roles
        embed = Embed(title='Below, you will see your current roles')
        description = ''
        for role in roles:
            description += f'{role.mention}\n'
        embed.description = description
        await interaction.followup.send('', wait=True, embed=embed)