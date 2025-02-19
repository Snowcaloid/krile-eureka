from uuid import uuid4
from discord import ButtonStyle, Embed, Message, TextChannel
from data.guilds.guild_channel import GuildChannel
from data.guilds.guild_message_functions import GuildMessageFunction
from data.guilds.guild_pings import GuildPingType
import data.cache.message_cache as cache
import bot
from data.events.event_category import EventCategory
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.ui.buttons import PartyLeaderButton, SendPLGuideButton, delete_buttons, save_buttons
from data.ui.views import PersistentView

class UIPLPost:
    """Party leader post."""
    async def create(self, guild_id: int, id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(id)
        if event is None or event.category == EventCategory.CUSTOM or not event.use_recruitment_posts: return
        channel_data = guild_data.channels.get(GuildChannelFunction.PL_CHANNEL, event.type)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        if channel is None: return
        pings = await guild_data.pings.get_mention_string(GuildPingType.PL_POST, event.type)
        message = await channel.send(pings, embed=Embed(description='...'))
        event.pl_post_id = message.id
        message = await self.rebuild(guild_id, id, True)
        guild_data.messages.add(message.id, channel.id, GuildMessageFunction.PL_POST)
        if event.use_recruitment_post_threads:
            await message.create_thread(name=event.recruitment_post_thread_title)


    async def rebuild(self, guild_id: int, id: int, recreate_view: bool = False) -> Message:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(id)
        if event is None or event.category == EventCategory.CUSTOM or not event.use_recruitment_posts: return
        channel_data = guild_data.channels.get(GuildChannelFunction.PL_CHANNEL, event.type)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        message = await cache.messages.get(event.pl_post_id, channel)
        if message is None: return
        embed = Embed(title=event.recruitment_post_title, description=event.recruitment_post_text)
        if recreate_view:
            delete_buttons(event.pl_post_id)
            view = PersistentView()
            bot.instance.data.ui.view.view_list.append(view)
            for i in range(1, 8):
                label = event.pl_button_texts[i-1]
                if label:
                    button = PartyLeaderButton(
                        label=label,
                        custom_id=str(uuid4()),
                        row=1 if i < 4 else 2,
                        index=i - 1 if i < 4 else i - 4,
                        style=ButtonStyle.primary if i < 4 else ButtonStyle.success if i != 7 else ButtonStyle.danger,
                        pl=i-1)
                    button.event_id = event.id
                    view.add_item(button)
            if event.category == EventCategory.BA:
                view.add_item(SendPLGuideButton(
                    label='How to party lead?',
                    custom_id=str(uuid4()),
                    row=1,
                    index=4,
                    style=ButtonStyle.gray))
            message = await message.edit(embed=embed, view=view)
            save_buttons(message, view)
        else:
            message = await message.edit(embed=embed)
        return message


    async def remove(self, guild_id: int, event_id: int) -> GuildChannel:
        guild_data = bot.instance.data.guilds.get(guild_id)
        event = guild_data.schedule.get(event_id)
        if event is None: return
        channel_data = guild_data.channels.get(GuildChannelFunction.PL_CHANNEL, event.type)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        message = await cache.messages.get(event.pl_post_id, channel)
        if message is None: return
        await message.delete()