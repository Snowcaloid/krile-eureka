from typing import Tuple
import aiohttp
from discord import ButtonStyle, Interaction, Message, SelectOption
from discord.ui import Button, Select

from utils.basic_types import EurekaTrackerZone
from utils.basic_types import GuildChannelFunction
from utils.basic_types import GuildPingType
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from data.ui.modals import EurekaTrackerModal
from data.ui.views import TemporaryView
from utils.logger import guild_log_message
from utils.functions import default_defer


class EurekaTrackerZoneSelect(Select):
    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    from data.ui.ui_eureka_info import UIEurekaInfoPost
    @UIEurekaInfoPost.bind
    def ui_eureka_info(self) -> UIEurekaInfoPost: ...

    def __init__(self, *, generate: bool = False):
        self.generate = generate
        self.message: Message = None
        options = [
            SelectOption(label='Anemos', value=str(EurekaTrackerZone.ANEMOS.value)),
            SelectOption(label='Pagos', value=str(EurekaTrackerZone.PAGOS.value)),
            SelectOption(label='Pyros', value=str(EurekaTrackerZone.PYROS.value)),
            SelectOption(label='Hydatos', value=str(EurekaTrackerZone.HYDATOS.value))
        ]
        super().__init__(placeholder="Select Eureka Instance",
                         options=options)


    async def generate_url(self, zone: EurekaTrackerZone) -> Tuple[str, str]:
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
        zone = EurekaTrackerZone(int(self.values[0]))
        if self.generate:
            await default_defer(interaction)
            url, passcode = await self.generate_url(zone)
            if next((tracker for tracker in self.eureka_info._trackers if tracker.url == url), None) is not None:
                self.eureka_info.remove(url)
            self.eureka_info.add(url, zone)
            await self.ui_eureka_info.rebuild(interaction.guild_id)
            view = TemporaryView()
            view.add_item(Button(url=url, label='Visit the tracker', style=ButtonStyle.link))
            await interaction.followup.send(content=f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view, ephemeral=True)
            await interaction.user.send(f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view)
            await guild_log_message(interaction.guild_id, f'{interaction.user.display_name} has added a tracker for {zone.name} - `{url}`.')
            notification_channel = GuildChannels(interaction.guild_id).get(GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION, str(zone.value))
            if notification_channel:
                channel = interaction.guild.get_channel(notification_channel.id)
                mentions = await GuildPings(interaction.guild_id).get_mention_string(GuildPingType.EUREKA_TRACKER_NOTIFICATION, str(zone.value))
                await channel.send(f'{mentions} Tracker {url} has been added for {zone.name} by {interaction.user.mention}.')
        else:
            await interaction.response.send_modal(EurekaTrackerModal(zone=zone))
        if self.message:
            await self.message.delete()