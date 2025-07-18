from __future__ import annotations
from re import search
from discord import ButtonStyle, HTTPException, Interaction, TextStyle
from discord.ui import Modal, TextInput, Button

from models.channel_assignment import ChannelAssignmentStruct
from models.role_assignment import RoleAssignmentStruct
from data_providers.channel_assignments import ChannelAssignmentProvider
from data_providers.role_assignments import RoleAssignmentsProvider
from utils.basic_types import EurekaInstance, RoleFunction
from utils.basic_types import ChannelFunction
from ui.views import TemporaryView
from utils.logger import guild_log_message

class EurekaTrackerModal(Modal):
    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    from ui.eureka_info import EurekaInfoPost
    @EurekaInfoPost.bind
    def ui_eureka_info(self) -> EurekaInfoPost: ...

    def __init__(self, *, zone: EurekaInstance = None) -> None:
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

        channel_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
            guild_id=interaction.guild_id,
            event_type=str(self.zone.value),
            function=ChannelFunction.EUREKA_TRACKER_NOTIFICATION
        ))
        if channel_struct:
            channel = interaction.guild.get_channel(channel_struct.channel_id)
            mention_string = RoleAssignmentsProvider().as_discord_mention_string(RoleAssignmentStruct(
                guild_id=interaction.guild_id,
                event_type=str(self.zone.value),
                function=RoleFunction.EUREKA_TRACKER_NOTIFICATION
            ))
            await channel.send(f'{mention_string} Tracker {url} has been added for {self.zone.name} by {interaction.user.mention}.')

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, HTTPException):
            await interaction.response.send_message(f" Value Error. Invalid URL",
                ephemeral=True)
        else:
            raise error