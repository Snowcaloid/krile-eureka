from discord import Embed, Message
import bot
from data.ui.buttons import ButtonType, MissedRunButton, button_custom_id
from data.ui.views import PersistentView


class UIMissedRunPost:
    """Message for application of missed run entries."""
    async def rebuild(self, guild_id: int, message: Message) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        if guild_data is None: return
        disclaimer = ''
        roles = guild_data.missed_runs.allowed_roles_as_string
        if roles:
            disclaimer = f'\n**Please note that this function is exclusive to members with following roles: {roles}.**'
        view = PersistentView()
        view.add_item(MissedRunButton(
            label='the button',
            custom_id=button_custom_id('missed', message, ButtonType.MISSEDRUN)))
        await message.edit(
            embed=Embed(title='Have you just missed this run?',
                        description=f'You can use the button in case you missed entrance to this run. This will save you to the list.{disclaimer}'),
            view=view)