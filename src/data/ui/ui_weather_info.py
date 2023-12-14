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
        embed = Embed(title='Eureka Weather info', description=(
            'Following information is displayed in your local time.\n'
            f'Current Eorzea time: {to_eorzea_time(datetime.utcnow()).strftime("%H:%M")}\n'
        ))
        embed.add_field(name='Anemos', value=(
            f'Current weather: {current_weather(EurekaZones.ANEMOS)}\n'
            f'{weather_emoji[EurekaWeathers.GALES]} Next Gales: {next_weather(EurekaZones.ANEMOS, EurekaWeathers.GALES)}\n'
        ))
        embed.add_field(name='Pagos', value=(
            f'Current weather: {current_weather(EurekaZones.PAGOS)}\n'
            f'{weather_emoji[EurekaWeathers.FOG]} Next Fog: {next_weather(EurekaZones.PAGOS, EurekaWeathers.FOG)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PAGOS, EurekaWeathers.BLIZZARDS)}\n'
        ))
        embed.add_field(name='Pyros', value=(
            f'Current weather: {current_weather(EurekaZones.PYROS)}\n'
            f'{weather_emoji[EurekaWeathers.HEATWAVES]} Next Heat Waves: {next_weather(EurekaZones.PYROS, EurekaWeathers.HEATWAVES)}\n'
            f'{weather_emoji[EurekaWeathers.BLIZZARDS]} Next Blizzards: {next_weather(EurekaZones.PYROS, EurekaWeathers.BLIZZARDS)}\n'
            f'{weather_emoji[EurekaWeathers.UMBRAL_WIND]} Next 3x Umbral Wind: {next_weather(EurekaZones.PYROS, EurekaWeathers.UMBRAL_WIND, 3)}\n'
        ))
        embed.add_field(name='Hydatos', value=(
            f'Current weather: {current_weather(EurekaZones.HYDATOS)}\n'
            f'{weather_emoji[EurekaWeathers.SNOW]} Next 3x Snow: {next_weather(EurekaZones.HYDATOS, EurekaWeathers.SNOW, 3)}\n'
        ))
        message = await message.edit(embed=embed)
        return await set_default_footer(message)


    async def remove(self, guild_id: int) -> None:
        guild_data = bot.instance.data.guilds.get(guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.WEATHER_POST)
        if message_data is None: return
        channel: TextChannel = bot.instance.get_channel(message_data.channel_id)
        message = await cache.messages.get(message_data.message_id, channel)
        if message is None: return
        await message.delete()