from datetime import datetime
from centralized_data import Bindable
from discord import Embed, Message, TextChannel
from utils.basic_types import MessageFunction
from data.guilds.guild_messages import GuildMessages
from data.weather.weather import EurekaWeathers, EurekaZones, current_weather, next_day, next_night, next_weather, to_eorzea_time, weather_emoji
from utils.functions import DiscordTimestampType, get_discord_timestamp

class UIWeatherPost(Bindable):
    """Eureka Weather Info post."""
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from data.cache.message_cache import MessageCache
    @MessageCache.bind
    def message_cache(self) -> MessageCache: ...

    async def rebuild(self, guild_id: int, message: Message = None) -> Message:
        if message is None:
            message_data = GuildMessages(guild_id).get(MessageFunction.WEATHER_POST)
            if message_data is None: return
            channel: TextChannel = self.bot._client.get_channel(message_data.channel_id)
            if channel is None: return
            message = await self.message_cache.get(message_data.message_id, channel)

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
        messages = GuildMessages(guild_id)
        message_data = messages.get(MessageFunction.WEATHER_POST)
        if message_data is None: return
        channel: TextChannel = self.bot._client.get_channel(message_data.channel_id)
        if channel is None: return
        message = await self.message_cache.get(message_data.message_id, channel)
        if message is None: return
        await message.delete()
        messages.remove(message_data.message_id)