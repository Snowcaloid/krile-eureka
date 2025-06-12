from datetime import datetime
from typing import override
from discord import Embed
from models.channel import ChannelStruct
from utils.basic_types import GuildChannelFunction, TaskExecutionType
from utils.basic_types import GuildPingType
from data.tasks.task import TaskTemplate


class Task_PostMainPasscode(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.POST_MAIN_PASSCODE

    @override
    def description(self, data: object, timestamp: datetime) -> str:
        return f'Post Main Passcode for event {data["entry_id"]} at {timestamp.strftime("%Y-%m %H:%M ST")}'

    @override
    async def execute(self, obj: object) -> None:
        """Sends the main party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            from data.events.schedule import Schedule
            from services.channels import ChannelsService
            from data.guilds.guild_pings import GuildPings

            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event is None: return
            channel_data = ChannelsService(obj["guild"]).find(
                ChannelStruct(
                    guild_id=obj["guild"],
                    function=GuildChannelFunction.PASSCODES,
                    event_type=event.type))
            if channel_data is None: return
            channel = self._bot.client.get_channel(channel_data.channel_id)
            if channel is None: return
            pings = await GuildPings(obj["guild"]).get_mention_string(GuildPingType.MAIN_PASSCODE, event.type)
            await channel.send(pings, embed=Embed(
                title=event.passcode_post_title,
                description=event.main_passcode_text))


