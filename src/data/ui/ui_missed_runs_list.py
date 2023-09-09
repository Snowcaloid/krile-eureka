from discord import Embed, TextChannel
import bot
import data.cache.message_cache as cache
from data.guilds.guild_channel_functions import GuildChannelFunction


class UIMissedRunsList:
    """Embed collection with data on all people who have missed runs."""
    async def rebuild(self, guild_id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        if guild_data is None: return
        channel_data = guild_data.channels.get(GuildChannelFunction.MISSED_POST_CHANNEL)
        if channel_data is None: return
        channel: TextChannel = bot.instance.get_channel(channel_data.id)
        if channel is None: return
        message = await cache.messages.get(guild_data.missed_runs.message_id, channel)
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
