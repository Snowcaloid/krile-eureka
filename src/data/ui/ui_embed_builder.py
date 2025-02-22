from centralized_data import Bindable
from discord import Embed, Interaction, Message

from data.ui.buttons import buttons_as_text, buttons_from_message
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
        await interaction.response.send_message(embed=self._generate_help_embed(),
            view=EmbedBuilderView(timeout=600, target=interaction))

    async def load(self, interaction: Interaction, message: Message):
        """Interactive Embed builder"""
        buttons = await buttons_from_message(message)
        if buttons:
            content = buttons_as_text(buttons)
        else:
            content = None
        await interaction.response.send_message(content, embed=message.embeds[0],
            view=EmbedBuilderView(timeout=600, target=interaction, buttons=buttons, embed=message.embeds[0]))