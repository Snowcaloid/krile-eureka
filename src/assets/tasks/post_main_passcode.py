from typing import override
from discord import Embed
import bot
from basic_types import GuildChannelFunction, TaskExecutionType
from basic_types import GuildPingType
from data.events.schedule import Schedule
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from data.tasks.task import TaskTemplate


class Task_PostMainPasscode(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.POST_MAIN_PASSCODE

    @override
    async def execute(self, obj: object) -> None:
        """Sends the main party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event is None: return
            channel_data = GuildChannels(obj["guild"]).get(GuildChannelFunction.PASSCODES, event.type)
            if channel_data is None: return
            guild = bot.instance.get_guild(obj["guild"])
            channel = guild.get_channel(channel_data.id)
            if channel is None: return
            pings = await GuildPings(obj["guild"]).get_mention_string(GuildPingType.MAIN_PASSCODE, event.type)
            await channel.send(pings, embed=Embed(
                title=event.passcode_post_title,
                description=event.main_passcode_text))


