from discord import ButtonStyle, Embed, Message, TextChannel
from data.eureka_info import EurekaTrackerZone
from data.guilds.guild_message_functions import GuildMessageFunction
import data.cache.message_cache as cache
import bot
from data.ui.buttons import AssignTrackerButton, GenerateTrackerButton, save_buttons
from data.ui.views import PersistentView
from data.weather.weather import EurekaWeathers, EurekaZones, next_4_weathers, next_weather, weather_emoji
from utils import DiscordTimestampType, get_discord_timestamp

class UIEurekaInfoPost:
    """Eureka Info post."""

    async def create(self, guild_id: int) -> Message:
        guild_data = bot.instance.data.guilds.get(guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.EUREKA_INFO)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        if channel is None: return
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return
        view = PersistentView()
        view.add_item(AssignTrackerButton(style=ButtonStyle.success, label='Assign an existing tracker', row=0, index=0))
        view.add_item(GenerateTrackerButton(style=ButtonStyle.primary, label='Generate a tracker', row=0, index=1))
        message = await message.edit(view=view)
        await self.rebuild(guild_id)
        save_buttons(message, view)

    def get_trackers_text(self, zone: EurekaTrackerZone) -> str:
        result = ''
        trackers = bot.instance.data.eureka_info.get(zone)
        if trackers:
            for tracker in trackers:
                result = result + f'* {tracker.url} [{get_discord_timestamp(tracker.timestamp, DiscordTimestampType.RELATIVE)}]\n'
        else:
            result = 'No tracker data.\n'
        return result

    async def rebuild(self, guild_id: int) -> Message:
        guild_data = bot.instance.data.guilds.get(guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.EUREKA_INFO)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        if channel is None: return
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return

        anemos_trackers = self.get_trackers_text(EurekaTrackerZone.ANEMOS)
        pagos_trackers = self.get_trackers_text(EurekaTrackerZone.PAGOS)
        pyros_trackers = self.get_trackers_text(EurekaTrackerZone.PYROS)
        hydatos_trackers = self.get_trackers_text(EurekaTrackerZone.HYDATOS)

        embed = Embed(title='Eureka Info', description=(
            f'## Anemos {next_4_weathers(EurekaZones.ANEMOS)}\n'
            f'Current Anemos Trackers:\n'
            f'{anemos_trackers}'
            f'{weather_emoji[EurekaWeathers.GALES]} Next Gales: {next_weather(EurekaZones.ANEMOS, EurekaWeathers.GALES)}\n'
            f'## Pagos {next_4_weathers(EurekaZones.PAGOS)}\n'
            f'Current Pagos Trackers:\n'
            f'{pagos_trackers}'
            f'{weather_emoji[EurekaWeathers.FOG]} Next Fog: {next_weather(EurekaZones.PAGOS, EurekaWeathers.FOG)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PAGOS, EurekaWeathers.BLIZZARDS)}\n'
            f'## Pyros {next_4_weathers(EurekaZones.PYROS)}\n'
            f'Current Pyros Trackers:\n'
            f'{pyros_trackers}'
            f'{weather_emoji[EurekaWeathers.HEATWAVES]} Next Heat Waves: {next_weather(EurekaZones.PYROS, EurekaWeathers.HEATWAVES)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PYROS, EurekaWeathers.BLIZZARDS)}\n'
            f'{weather_emoji[EurekaWeathers.UMBRAL_WIND]} Next 2x Umbral Wind: {next_weather(EurekaZones.PYROS, EurekaWeathers.UMBRAL_WIND, 2)}\n'
            f'## Hydatos {next_4_weathers(EurekaZones.HYDATOS)}\n'
            f'Current Hydatos Trackers:\n'
            f'{hydatos_trackers}'
            f'{weather_emoji[EurekaWeathers.SNOW]} Next 2x Snow: {next_weather(EurekaZones.HYDATOS, EurekaWeathers.SNOW, 2)}'
        ))
        return await message.edit(embed=embed)


    async def remove(self, guild_id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.EUREKA_INFO)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        if channel is None: return
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return
        await message.delete()
        guild_data.messages.remove(message_data.message_id)