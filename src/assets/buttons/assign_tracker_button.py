from typing import override
from models.button.discord_button import DiscordButton
from models.button.button_template import ButtonTemplate
from utils.basic_types import ButtonType
from ui.selects import EurekaTrackerZoneSelect
from ui.views import TemporaryView


from discord import Interaction


class AssignTrackerButton(ButtonTemplate):
    """Buttons which show a modal for url of a tracker"""

    def button_type(self) -> ButtonType: return ButtonType.ASSIGN_TRACKER

    @override
    async def callback(self, interaction: Interaction, button: DiscordButton):
        view = TemporaryView()
        select = EurekaTrackerZoneSelect(generate=False)
        view.add_item(select)
        select.message = await interaction.response.send_message('Select a Eureka region, then paste the tracker ID.', view=view, ephemeral=True)