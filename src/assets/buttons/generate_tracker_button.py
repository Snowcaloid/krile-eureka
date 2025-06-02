from typing import override
from ui.base_button import BaseButton, ButtonTemplate
from utils.basic_types import ButtonType
from ui.selects import EurekaTrackerZoneSelect
from ui.views import TemporaryView

from discord import Interaction


class GenerateTrackerButton(ButtonTemplate):
    """Buttons which generates a new url for a tracker"""

    def button_type(self) -> ButtonType: return ButtonType.GENERATE_TRACKER

    @override
    async def callback(self, interaction: Interaction, button: BaseButton):
        view = TemporaryView()
        select = EurekaTrackerZoneSelect(generate=True)
        view.add_item(select)
        select.message = await interaction.response.send_message('Select a Eureka region.', view=view, ephemeral=True)