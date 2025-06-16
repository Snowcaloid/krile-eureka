from typing import override
from discord import Button, Interaction

from models.button import ButtonStruct
from models.button.button_template import ButtonTemplate
from models.button.button_template import ButtonTemplates
from discord.ui import Button


class DiscordButton(Button):
    struct: ButtonStruct
    template: ButtonTemplate

    @ButtonTemplates.bind
    def button_templates(self) -> ButtonTemplates: return ...

    def __init__(self,
                 button_struct: ButtonStruct,
                 *,
                 disabled: bool = False,
                 ):
        self.struct = button_struct
        self.template: ButtonTemplate = self.button_templates.get(button_struct.button_type)
        super().__init__(style=button_struct.style,label=button_struct.label,disabled=disabled,custom_id=button_struct.button_id,
                         row=button_struct.row,emoji=button_struct.emoji)

    @override
    async def callback(self, interaction: Interaction):
        if self.struct.message_id is None or interaction.message.id == self.struct.message_id:
            await self.template.callback(interaction, self)
