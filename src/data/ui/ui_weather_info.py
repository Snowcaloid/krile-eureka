from datetime import datetime
from discord import Embed, Message, TextChannel
from data.guilds.guild_message_functions import GuildMessageFunction
import data.cache.message_cache as cache
import bot
from data.weather.weather import EurekaWeathers, EurekaZones, current_weather, next_weather, to_eorzea_time, weather_emoji
from utils import set_default_footer

class UIWeatherPost:
    """Eureka Weather Info post."""

    async def rebuild(self, guild_id: int) -> Message:
        guild_data = bot.instance.data.guilds.get(guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.WEATHER_POST)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        if channel is None: return
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return
        current_time = to_eorzea_time(datetime.utcnow())
        emoji = ':crescent_moon:' if current_time.hour > 17 or current_time.hour < 6 else ':sun:'
        embed = Embed(title='Eureka Weather info', description=(
            'The post is updated every minute and is therefore the time displayed below might be a bit delayed.\n'
            'Following information is displayed in your local time.\n'
            f'Current Eorzea time: {emoji} {current_time.strftime("%H:%M")}\n\n'
            f'**Anemos - {current_weather(EurekaZones.ANEMOS)}**\n'
            f'{weather_emoji[EurekaWeathers.GALES]} Next Gales: {next_weather(EurekaZones.ANEMOS, EurekaWeathers.GALES)}\n\n'
            f'**Pagos - {current_weather(EurekaZones.PAGOS)}**\n'
            f'{weather_emoji[EurekaWeathers.FOG]} Next Fog: {next_weather(EurekaZones.PAGOS, EurekaWeathers.FOG)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PAGOS, EurekaWeathers.BLIZZARDS)}\n\n'
            f'**Pyros - {current_weather(EurekaZones.PYROS)}**\n'
            f'{weather_emoji[EurekaWeathers.HEATWAVES]} Next Heat Waves: {next_weather(EurekaZones.PYROS, EurekaWeathers.HEATWAVES)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PYROS, EurekaWeathers.BLIZZARDS)}\n'
            f'{weather_emoji[EurekaWeathers.UMBRAL_WIND]} Next 2x Umbral Wind: {next_weather(EurekaZones.PYROS, EurekaWeathers.UMBRAL_WIND, 2)}\n\n'
            f'**Hydatos - {current_weather(EurekaZones.HYDATOS)}**\n'
            f'{weather_emoji[EurekaWeathers.SNOW]} Next 2x Snow: {next_weather(EurekaZones.HYDATOS, EurekaWeathers.SNOW, 2)}\n'
        ))
        message = await message.edit(embed=embed)
        return await set_default_footer(message)


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