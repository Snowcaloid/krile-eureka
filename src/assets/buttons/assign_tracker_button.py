from typing import override
from data.ui.base_button import BaseButton, ButtonTemplate
from utils.basic_types import ButtonType
from data.ui.selects import EurekaTrackerZoneSelect
from data.ui.views import TemporaryView


from discord import Interaction


class AssignTrackerButton(ButtonTemplate):
    """Buttons which show a modal for url of a tracker"""

    def button_type(self) -> ButtonType: return ButtonType.ASSIGN_TRACKER

    @override
    async def callback(self, interaction: Interaction, button: BaseButton):
        view = TemporaryView()
        select = EurekaTrackerZoneSelect(generate=False)
        view.add_item(select)
        select.message = await interaction.response.send_message('Select a Eureka region, then paste the tracker ID.', view=view, ephemeral=True)