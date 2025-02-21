from typing import override
from discord import Embed
import bot
from data.guilds.guild import Guilds
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.tasks.task import TaskExecutionType, TaskTemplate


class Task_PostMainPasscode(TaskTemplate):
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.POST_MAIN_PASSCODE

    @override
    async def execute(self, obj: object) -> None:
        """Sends the main party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            guild_data = self.guilds.get(["guild"])
            if guild_data is None: return
            event = guild_data.schedule.get(obj["entry_id"])
            if event is None: return
            channel_data = guild_data.channels.get(GuildChannelFunction.PASSCODES, event.type)
            if channel_data is None: return
            guild = bot.instance.get_guild(guild_data.id)
            channel = guild.get_channel(channel_data.id)
            if channel is None: return
            pings = await guild_data.pings.get_mention_string(GuildPingType.MAIN_PASSCODE, event.type)
            await channel.send(pings, embed=Embed(
                title=event.passcode_post_title,
                description=event.main_passcode_text))


