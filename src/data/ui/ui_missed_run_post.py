from uuid import uuid4
from discord import Embed, Message
import bot
from data.ui.buttons import ButtonType, MissedRunButton
from data.ui.views import PersistentView


class UIMissedRunPost:
    """Message for application of missed run entries."""
    async def rebuild(self, guild_id: int, message: Message, event_category: str) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        if guild_data is None: return
        disclaimer = f'\n**Please note that this function is exclusive to members with certain roles.**'
        view = PersistentView()
        button = MissedRunButton(label='The Button', custom_id=str(uuid4()))
        button.event_category = event_category
        view.add_item(button)
        await message.edit(
            embed=Embed(title='Have you just missed this run?',
                        description=f'You can use the button in case you missed entrance to this run. This will save you to the list.{disclaimer}'),
            view=view)