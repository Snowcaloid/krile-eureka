from typing import override
from discord import Embed
from utils.basic_types import GuildChannelFunction, TaskExecutionType
from utils.basic_types import GuildPingType
from data.events.schedule import Schedule
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from data.tasks.task import TaskTemplate


class Task_PostSupportPasscode(TaskTemplate):
    from bot import DiscordClient
    @DiscordClient.bind
    def client(self) -> DiscordClient: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.POST_SUPPORT_PASSCODE

    @override
    async def execute(self, obj: object) -> None:
        """Sends the support party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event is None: return
            channel_data = GuildChannels(obj["guild"]).get(GuildChannelFunction.SUPPORT_PASSCODES, event.type)
            if channel_data is None: return
            guild = self.client.get_guild(obj["guild"])
            channel = guild.get_channel(channel_data.id)
            if channel is None: return
            pings = await GuildPings(obj["guild"]).get_mention_string(GuildPingType.SUPPORT_PASSCODE, event.type)
            await channel.send(pings, embed=Embed(
                title=event.passcode_post_title,
                description=event.support_passcode_text))


