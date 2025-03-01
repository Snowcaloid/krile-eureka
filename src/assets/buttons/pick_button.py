
from typing import override
from data.ui.base_button import BaseButton, ButtonTemplate
from basic_types import ButtonType


from discord import Interaction

from external.Obryt.embed import AddButtonModal
from external.Obryt.utils.constants import EMOJIS


class PickButton(ButtonTemplate):
    """Pick the placement for a button in the Button Matrix."""

    @override
    def button_type(self) -> ButtonType: return ButtonType.PICK_BUTTON

    @override
    async def callback(self, interaction: Interaction, button: BaseButton):
        if button.disabled: return
        if button.original_button is None:
            await interaction.response.send_modal(AddButtonModal(
                buttons=button.matrix, button=button, parent_view=button.parent_view))
        else:
            moving_button = button.original_button
            button.matrix[moving_button.row][moving_button.index] = None
            moving_button.row = button.row
            moving_button.index = button.index
            button.matrix[moving_button.row][moving_button.index] = moving_button
            button.parent_view.message = await button.parent_view.message.edit(view=button.matrix.as_view())
            del button # just in case
            await interaction.response.edit_message(content=f'{EMOJIS["yes"]} Button moved successfully.', view=None)