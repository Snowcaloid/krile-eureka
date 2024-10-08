from typing import Tuple
import aiohttp
from discord import ButtonStyle, Interaction, Message, SelectOption
from discord.ui import Button, Select

import bot
from data.eureka_info import EurekaTrackerZone
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.ui.modals import EurekaTrackerModal
from data.ui.views import TemporaryView
from logger import guild_log_message
from utils import default_defer


class EurekaTrackerZoneSelect(Select):
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
            eureka = bot.instance.data.eureka_info
            if next((tracker for tracker in eureka._trackers if tracker.url == url), None) is not None:
                eureka.remove(url)
            bot.instance.data.eureka_info.add(url, zone)
            await bot.instance.data.ui.eureka_info.rebuild(interaction.guild_id)
            view = TemporaryView()
            view.add_item(Button(url=url, label='Visit the tracker', style=ButtonStyle.link))
            await interaction.followup.send(content=f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view, ephemeral=True)
            await interaction.user.send(f'Successfully generated {zone.name} tracker. Passcode: {passcode}', view=view)
            await guild_log_message(interaction.guild_id, f'{interaction.user.display_name} has added a tracker for {zone.name} - `{url}`.')
            guild = bot.instance.data.guilds.get(interaction.guild_id)
            if guild:
                notification_channel = guild.channels.get(GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION, str(zone.value))
                if notification_channel:
                    channel = interaction.guild.get_channel(notification_channel.id)
                    mentions = await guild.pings.get_mention_string(GuildPingType.EUREKA_TRACKER_NOTIFICATION, str(zone.value))
                    await channel.send(f'{mentions} Tracker {url} has been added for {zone.name} by {interaction.user.mention}.')
        else:
            await interaction.response.send_modal(EurekaTrackerModal(zone=zone))
        if self.message:
            await self.message.delete()