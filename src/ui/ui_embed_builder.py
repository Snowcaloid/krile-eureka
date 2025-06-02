from centralized_data import Bindable
from discord import Embed, Interaction, Message

from ui.base_button import ButtonMatrix
from external.Obryt.embed import EmbedBuilderView
from external.Obryt.utils.constants import CONTRAST_COLOR

class UI_Embed_Builder(Bindable):
    def _generate_help_embed(self) -> Embed:
        emb = Embed(title="Title",
            url="http://example.com/students-of-baldesion",
            description="This is the _description_ of the embed.\n"
            "Descriptions can be upto **4000** characters long.\n"
            "There is a shared limit of **6000** characters (including fields) for the embed.\n"
            "Note that the description can be __split into multiple lines.__\n",
            color=CONTRAST_COLOR)
        emb.set_author(name="<< Author Icon | Author Name",
            url="http://example.com/students-of-baldesion",
            icon_url="https://i.imgur.com/KmwxpHF.png")
        emb.set_footer(text="<< Footer Icon | This is the footer",
            icon_url="https://i.imgur.com/V8xDSE5.png")
        for i in range(1, 3):
            emb.add_field(name=f"Field {i}", value=f"Field {i} Value\nIt's Inline", inline=True)
        emb.add_field(name=f"Field 3", value=f"Field 3 Value\nIt's NOT Inline", inline=False)
        emb.set_image(url="https://i.imgur.com/EhtHWap.png")
        emb.set_thumbnail(url="https://i.imgur.com/hq8nDF2.png")

        return emb

    async def create(self, interaction: Interaction):
        """Interactive Embed builder"""
        message = await interaction.channel.send(embed=self._generate_help_embed())
        await interaction.response.send_message(
            view=EmbedBuilderView(timeout=None, target=interaction, message=message, buttons=ButtonMatrix([])))

    async def load(self, interaction: Interaction, original_message: Message):
        """Interactive Embed builder"""
        buttons = await ButtonMatrix.from_message(original_message)
        buttons.disabled = True
        message = await interaction.channel.send(embed=original_message.embeds[0], view=buttons.as_view())
        await interaction.response.send_message(
            view=EmbedBuilderView(timeout=None,
                                  target=interaction,
                                  buttons=buttons,
                                  embed=original_message.embeds[0],
                                  message=message))