from discord import Embed, TextChannel
from data.guilds.guild_pings import GuildPingType
import data.cache.message_cache as cache
import bot
from data.events.event import EventCategory
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.ui.buttons import ButtonType, PartyLeaderButton, button_custom_id
from data.ui.views import PersistentView
from utils import set_default_footer

class UIPLPost:
    """Party leader post."""
    async def create(self, guild_id: int, id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(id)
        if event is None or event.category == EventCategory.CUSTOM: return
        channel_data = guild_data.channels.get(GuildChannelFunction.PL_CHANNEL, event.type)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        if channel is None: return
        pings = await guild_data.pings.get_mention_string(guild_id, GuildPingType.PL_POST, event.type)
        message = await channel.send(f'{pings} Recruitment post #{str(id)}')
        event.pl_post_id = message.id
        view = PersistentView()
        for i in range(1, 8):
            label = event.pl_button_texts[i-1]
            if label:
                view.add_item(PartyLeaderButton(
                    label=label,
                    custom_id=button_custom_id(f'pl{i}', message, ButtonType.PL_POST), row=1 if i < 4 else 2))
        await self.rebuild(guild_id, id, view)
        if event.use_pl_post_thread:
            await message.create_thread(name=event.pl_post_thread_title)


    async def rebuild(self, guild_id: int, id: int, view: PersistentView = None) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(id)
        if event is None or event.category == EventCategory.CUSTOM: return
        channel_data = guild_data.channels.get(GuildChannelFunction.PL_CHANNEL, event.type)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        message = await cache.messages.get(event.pl_post_id, channel)
        if message is None: return
        embed = Embed(title=event.pl_post_title, description=event.pl_post_text)
        if view:
            message = await message.edit(embed=embed, view=view)
        else:
            message = await message.edit(embed=embed)
        await set_default_footer(message)