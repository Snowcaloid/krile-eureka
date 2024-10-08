from datetime import datetime
from discord import Embed, Message, TextChannel
from data.guilds.guild_message_functions import GuildMessageFunction
import data.cache.message_cache as cache
import bot
from data.weather.weather import EurekaWeathers, EurekaZones, current_weather, next_day, next_night, next_weather, to_eorzea_time, weather_emoji
from utils import DiscordTimestampType, get_discord_timestamp

class UIWeatherPost:
    """Eureka Weather Info post."""

    async def rebuild(self, guild_id: int, message: Message = None) -> Message:
        if message is None:
            guild_data = bot.instance.data.guilds.get(guild_id)
            message_data = guild_data.messages.get(GuildMessageFunction.WEATHER_POST)
            if message_data is None: return
            channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
            if channel is None: return
            message = await cache.messages.get(message_data.message_id, channel)

        if message is None: return
        current_time = to_eorzea_time(datetime.utcnow())
        is_night = current_time.hour > 17 or current_time.hour < 6
        if is_night:
            emoji_current = ':crescent_moon:'
            next_day_or_night = ':sunny: Next day '
            next_day_or_night_time = next_day()
        else:
            emoji_current = ':sunny:'
            next_day_or_night = ':crescent_moon: Next night '
            next_day_or_night_time = next_night()

        embed = Embed(title='Eureka Weather info', description=(
            f'Current Eorzea time: {emoji_current} {current_time.strftime("%H:%M")}\n'
            f'{next_day_or_night} {get_discord_timestamp(next_day_or_night_time, DiscordTimestampType.RELATIVE)}\n\n'
            f'**Anemos {current_weather(EurekaZones.ANEMOS)}**\n'
            f'{weather_emoji[EurekaWeathers.GALES]} Next Gales: {next_weather(EurekaZones.ANEMOS, EurekaWeathers.GALES)}\n\n'
            f'**Pagos {current_weather(EurekaZones.PAGOS)}**\n'
            f'{weather_emoji[EurekaWeathers.FOG]} Next Fog: {next_weather(EurekaZones.PAGOS, EurekaWeathers.FOG)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PAGOS, EurekaWeathers.BLIZZARDS)}\n\n'
            f'**Pyros {current_weather(EurekaZones.PYROS)}**\n'
            f'{weather_emoji[EurekaWeathers.HEATWAVES]} Next Heat Waves: {next_weather(EurekaZones.PYROS, EurekaWeathers.HEATWAVES)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PYROS, EurekaWeathers.BLIZZARDS)}\n'
            f'{weather_emoji[EurekaWeathers.UMBRAL_WIND]} Next 2x Umbral Wind: {next_weather(EurekaZones.PYROS, EurekaWeathers.UMBRAL_WIND, 2)}\n\n'
            f'**Hydatos {current_weather(EurekaZones.HYDATOS)}**\n'
            f'{weather_emoji[EurekaWeathers.SNOW]} Next 2x Snow: {next_weather(EurekaZones.HYDATOS, EurekaWeathers.SNOW, 2)}\n'
        ))
        message = await message.edit(embed=embed)


    async def remove(self, guild_id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.WEATHER_POST)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        if channel is None: return
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return
        await message.delete()
        guild_data.messages.remove(message_data.message_id)