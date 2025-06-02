from ui.base_button import BaseButton, ButtonTemplate
from utils.basic_types import ButtonType
from utils.logger import feedback_and_log
from utils.functions import default_defer, default_response

from discord import Interaction, Member

class RoleSelectionButton(ButtonTemplate):
    """Buttons, which add or remove a role from the user who interacts with them"""

    def button_type(self) -> ButtonType: return ButtonType.ROLE_SELECTION

    async def callback(self, interaction: Interaction, button: BaseButton):
        await default_defer(interaction)
        if isinstance(interaction.user, Member):
            if button.role is None:
                await feedback_and_log(interaction, f'tried using button <{button.label}> in message <{button.message.jump_url}> but role is not loaded. Contact your administrators.')
            elif interaction.user.get_role(button.role.id):
                await interaction.user.remove_roles(button.role)
                await feedback_and_log(interaction, f'removed role **{button.role.name}** from {interaction.user.mention}.')
            else:
                await interaction.user.add_roles(button.role)
                await feedback_and_log(interaction, f'taken the role **{button.role.name}**.')
        else:
            await default_response(interaction, f'Role buttons don''t work outside of a server setting.')