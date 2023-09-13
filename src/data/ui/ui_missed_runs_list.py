from discord import Embed, Message, TextChannel
import bot
import data.cache.message_cache as cache
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_message_functions import GuildMessageFunction


class UIMissedRunsList:
    async def create(self, guild_id: int, event_category: str) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        if guild_data is None: return
        channel_data = guild_data.channels.get(GuildChannelFunction.MISSED_POST_CHANNEL, event_category)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        if channel is None: return
        message: Message = await channel.send(embed=Embed(description='...'))
        old_message_data = guild_data.messages.get(GuildMessageFunction.MISSED_RUNS_LIST, event_category)
        if old_message_data:
            old_channel = bot.instance.get_channel(old_message_data.channel_id)
            if old_channel:
                old_message = await cache.messages.get(old_message_data.message_id, old_channel)
                if old_message:
                    await old_message.delete()
            guild_data.messages.remove(old_message_data.message_id) # TODO: this code is a code duplicate
        guild_data.messages.add(message.id, channel.id, GuildMessageFunction.MISSED_RUNS_LIST, event_category)
        await self.rebuild(guild_id, event_category)

    """Embed collection with data on all people who have missed runs."""
    async def rebuild(self, guild_id: int, event_category: str) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        if guild_data is None: return
        message_data = guild_data.messages.get(GuildMessageFunction.MISSED_RUNS_LIST, event_category)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        if channel is None: return
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return
        embeds = []
        embed = Embed(title='List of people with missing runs')
        embeds.append(embed)
        i = 0
        description = ''
        guild = bot.instance.get_guild(guild_id)
        for missed_data in guild_data.missed_runs.all:
            i += 1
            if i % 150 == 0:
                embed.description = description.strip()
                embed = Embed(description='...')
                embeds.append(embed)
                description = ''
            member = guild.get_member(missed_data.user)
            if member:
                description = "\n".join([description, f'{str(missed_data.amount)} - {member.display_name}'])
        if description:
            embed.description = description.strip()

        await message.edit(embeds=embeds)
