from discord import Embed
import bot
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_PostSupportPasscode(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.POST_SUPPORT_PASSCODE

    @classmethod
    async def execute(cl, obj: object) -> None:
        """Sends the support party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            guild_data = bot.instance.data.guilds.get(obj["guild"])
            if guild_data is None: return
            event = guild_data.schedule.get(obj["entry_id"])
            if event is None or event.is_signup: return
            channel_data = guild_data.channels.get(GuildChannelFunction.SUPPORT_PASSCODES, event.type)
            if channel_data is None: return
            guild = bot.instance.get_guild(guild_data.id)
            channel = guild.get_channel(channel_data.id)
            if channel is None: return
            pings = await guild_data.pings.get_mention_string(GuildPingType.SUPPORT_PASSCODE, event.type)
            message = await channel.send(pings, embed=Embed(
                title=event.passcode_post_title,
                description=event.support_passcode_text))


