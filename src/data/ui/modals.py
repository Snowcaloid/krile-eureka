from __future__ import annotations
from re import search
from discord import ButtonStyle, HTTPException, Interaction, TextStyle
from discord.ui import Modal, TextInput, Button

from utils.basic_types import EurekaTrackerZone
from utils.basic_types import GuildChannelFunction
from utils.basic_types import GuildPingType
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from data.ui.views import TemporaryView
from utils.logger import guild_log_message

class EurekaTrackerModal(Modal):
    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    from data.ui.ui_eureka_info import UIEurekaInfoPost
    @UIEurekaInfoPost.bind
    def ui_eureka_info(self) -> UIEurekaInfoPost: ...

    def __init__(self, *, zone: EurekaTrackerZone = None) -> None:
        self.zone = zone
        super().__init__(title="Enter tracker URL or ID", timeout=None)

    url = TextInput(
        label="Tracker URL or ID",
        style=TextStyle.short,
        placeholder="https://ffxiv-eureka.com/")

    async def on_submit(self, interaction: Interaction) -> None:
        url = self.url.value
        # URL -> Last 6 characters have to be the ID
        if url.startswith('https://ffxiv-eureka.com/') and search('[A-Za-z0-9_-]{6}', url[len('https://ffxiv-eureka.com/'):]).group(0) == url[-6:]:
            pass
        elif len(url) == 6 and search('[A-Za-z0-9_-]{6}', url).group(0) == url:
            url = f'https://ffxiv-eureka.com/{url}'
        else:
            raise ValueError('Invalid URL or ID')

        if next((tracker for tracker in self.eureka_info._trackers if tracker.url == url), None) is not None:
            self.eureka_info.remove(url)
        self.eureka_info.add(url, self.zone)
        await self.ui_eureka_info.rebuild(interaction.guild_id)
        view = TemporaryView()
        view.add_item(Button(url=url, label='Visit the tracker', style=ButtonStyle.link))
        await interaction.response.edit_message(content='Successfully assigned tracker.', view=view)
        await guild_log_message(interaction.guild_id, f'{interaction.user.display_name} has added a tracker for {self.zone.name} - `{url}`.')

        notification_channel = GuildChannels(interaction.guild_id).get(GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION, str(self.zone.value))
        if notification_channel:
            channel = interaction.guild.get_channel(notification_channel.id)
            mentions = await GuildPings(interaction.guild_id).get_mention_string(GuildPingType.EUREKA_TRACKER_NOTIFICATION, str(self.zone.value))
            await channel.send(f'{mentions} Tracker {url} has been added for {self.zone.name} by {interaction.user.mention}.')

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, HTTPException):
            await interaction.response.send_message(f" Value Error. Invalid URL",
                ephemeral=True)
        else:
            raise error