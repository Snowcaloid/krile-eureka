from uuid import uuid4
from centralized_data import Bindable
from discord import ButtonStyle, Embed, Message, TextChannel
from data_providers.message_assignments import MessageAssignmentsProvider
from models.button import ButtonStruct
from models.button.discord_button import DiscordButton
from models.message_assignment import MessageAssignmentStruct
from utils.basic_types import EurekaInstance
from utils.basic_types import MessageFunction
from ui.base_button import save_buttons
from utils.basic_types import ButtonType
from ui.views import PersistentView
from data.weather.weather import EurekaWeathers, EurekaZones, next_4_weathers, next_weather, weather_emoji
from utils.functions import DiscordTimestampType, get_discord_timestamp

class EurekaInfoPost(Bindable):
    """Eureka Info post."""
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    def _embed(self) -> Embed:
        anemos_trackers = self.get_trackers_text(EurekaInstance.ANEMOS)
        pagos_trackers = self.get_trackers_text(EurekaInstance.PAGOS)
        pyros_trackers = self.get_trackers_text(EurekaInstance.PYROS)
        hydatos_trackers = self.get_trackers_text(EurekaInstance.HYDATOS)

        return Embed(title='Eureka Info', description=(
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

    async def create(self, channel: TextChannel) -> Message:
        view = PersistentView()
        view.add_item(DiscordButton(button_struct=ButtonStruct(
            button_type=ButtonType.ASSIGN_TRACKER,
            style=ButtonStyle.success,
            label='Assign an existing tracker',
            row=0, index=0,
            button_id=str(uuid4())
        )))
        view.add_item(DiscordButton(button_struct=ButtonStruct(
            button_type=ButtonType.GENERATE_TRACKER,
            style=ButtonStyle.primary,
            label='Generate a tracker',
            row=0, index=1,
            button_id=str(uuid4())
        )))
        message = await channel.send(view=view, embed=self._embed())
        save_buttons(message, view)
        return await channel.fetch_message(message.id)

    def get_trackers_text(self, zone: EurekaInstance) -> str:
        result = ''
        trackers = self.eureka_info.get(zone)
        if trackers:
            for tracker in trackers:
                result = result + f'* {tracker.url} [{get_discord_timestamp(tracker.timestamp, DiscordTimestampType.RELATIVE)}]\n'
        else:
            result = 'No tracker data.\n'
        return result

    async def rebuild(self, guild_id: int) -> None:
        message_assignment_struct = MessageAssignmentsProvider().find(MessageAssignmentStruct(
            guild_id=guild_id,
            function=MessageFunction.EUREKA_INSTANCE_INFO
        ))
        if not message_assignment_struct: return
        message = await self.bot.get_text_channel(message_assignment_struct.channel_id).fetch_message(message_assignment_struct.message_id)
        if not message: return
        await message.edit(embed=self._embed())
