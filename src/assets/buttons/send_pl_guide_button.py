from models.button.discord_button import DiscordButton
from models.button.button_template import ButtonTemplate
from utils.basic_types import ButtonType
from utils.functions import default_defer, default_response


from discord import Interaction


class SendPLGuideButton(ButtonTemplate):
    """Buttons which sends a party leading guide to the user"""

    def button_type(self) -> ButtonType: return ButtonType.SEND_PL_GUIDE

    from ui.ui_help import UIHelp
    @UIHelp.bind
    def ui_help(self) -> UIHelp: ...

    async def callback(self, interaction: Interaction, button: DiscordButton):
        await default_defer(interaction)
        message = await interaction.user.send('_ _')
        await self.ui_help.ba_party_leader(message, interaction.guild.emojis)
        await default_response(interaction, 'The guide has been sent to your DMs.')