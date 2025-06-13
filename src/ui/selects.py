from typing import Tuple
import aiohttp
from discord import ButtonStyle, Interaction, Message, SelectOption
from discord.ui import Button, Select

from models.channel import ChannelStruct
from models.roles import RoleStruct
from providers.roles import RolesProvider
from services.channels import ChannelsService
from utils.basic_types import EurekaInstance, RoleFunction
from utils.basic_types import GuildChannelFunction
from ui.modals import EurekaTrackerModal
from ui.views import TemporaryView
from utils.logger import guild_log_message
from utils.functions import default_defer


class EurekaTrackerZoneSelect(Select):
    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def _eureka_info(self) -> EurekaInfo: ...

    from ui.ui_eureka_info import UIEurekaInfoPost
    @UIEurekaInfoPost.bind
    def _ui_eureka_info(self) -> UIEurekaInfoPost: ...

    def __init__(self, *, generate: bool = False):
        self.generate = generate
        self.message: Message = None
        options = [
            SelectOption(label='Anemos', value=str(EurekaInstance.ANEMOS.value)),
            SelectOption(label='Pagos', value=str(EurekaInstance.PAGOS.value)),
            SelectOption(label='Pyros', value=str(EurekaInstance.PYROS.value)),
            SelectOption(label='Hydatos', value=str(EurekaInstance.HYDATOS.value))
        ]
        super().__init__(placeholder="Select Eureka Instance",
                         options=options)


    async def generate_url(self, zone: EurekaInstance) -> Tuple[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://ffxiv-eureka.com/api/instances', json=
                {
                    "data": {
                        "attributes": {
                            "copy-from": None,
                            "data-center-id": None,
                            "instance-id": None,
                            "created-at": None,
                            "updated-at": None,
                            "zone-id": str(zone.value)
                        },
                        "type": "instances"
                    }
                }) as resp:
                json = await resp.json()
                if json and json["data"] and json["data"]["id"]:
                    if json["data"]["attributes"] and json["data"]["attributes"]["password"]:
                        return f'https://ffxiv-eureka.com/{json["data"]["id"]}', json["data"]["attributes"]["password"]
                return '', ''


    async def callback(self, interaction: Interaction):
        # check if user has access to send messages to channel
        zone = EurekaInstance(int(self.values[0]))
        if self.generate:
            await default_defer(interaction)
            url, passcode = await self.generate_url(zone)
            if next((tracker for tracker in self._eureka_info._trackers if tracker.url == url), None) is not None:
                self._eureka_info.remove(url)
            self._eureka_info.add(url, zone)
            await self._ui_eureka_info.rebuild(interaction.guild_id)
            view = TemporaryView()
            view.add_item(Button(url=url, label='Visit the tracker', style=ButtonStyle.link))
            await interaction.followup.send(content=f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view, ephemeral=True)
            await interaction.user.send(f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view)
            await guild_log_message(interaction.guild_id, f'{interaction.user.display_name} has added a tracker for {zone.name} - `{url}`.')
            channel_struct = ChannelsService(interaction.guild_id).find(ChannelStruct(
                guild_id=interaction.guild_id,
                function=GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION,
                event_type=str(zone.value)
            ))
            if channel_struct:
                channel = interaction.guild.get_channel(channel_struct.channel_id)
                mention_string = RolesProvider().as_discord_mention_string(RoleStruct(
                    guild_id=interaction.guild_id,
                    event_type=str(zone.value),
                    function=RoleFunction.EUREKA_TRACKER_NOTIFICATION_PING
                ))
                await channel.send(f'{mention_string} Tracker {url} has been added for {zone.name} by {interaction.user.mention}.')
        else:
            await interaction.response.send_modal(EurekaTrackerModal(zone=zone))
        if self.message:
            await self.message.delete()