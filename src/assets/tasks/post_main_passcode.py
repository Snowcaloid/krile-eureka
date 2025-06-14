from datetime import datetime
from typing import override
from discord import Embed, TextChannel
from models.channel_assignment import ChannelAssignmentStruct
from utils.basic_types import GuildChannelFunction, RoleFunction, TaskExecutionType
from tasks.task import TaskTemplate


class Task_PostMainPasscode(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.POST_MAIN_PASSCODE

    @override
    def description(self, data: dict, timestamp: datetime) -> str:
        return f'Post Main Passcode for event {data["entry_id"]} at {timestamp.strftime("%Y-%m %H:%M ST")}'

    @override
    async def execute(self, obj: dict) -> None:
        """Sends the main party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            from data.events.schedule import Schedule
            from data_providers.channel_assignments import ChannelAssignmentProvider
            from data_writers.roles import RolesProvider
            from models.roles import RoleStruct

            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event is None: return
            channel_struct = ChannelAssignmentProvider().find(
                ChannelAssignmentStruct(
                    guild_id=obj["guild"],
                    function=GuildChannelFunction.PASSCODES,
                    event_type=event.type))
            if channel_struct is None: return
            channel = self._bot._client.get_channel(channel_struct.channel_id)
            if not isinstance(channel, TextChannel): return
            mention_string = RolesProvider().as_discord_mention_string(RoleStruct(
                guild_id=obj["guild"],
                event_category=event.type,
                function=RoleFunction.MAIN_PASSCODE_PING
            ))
            await channel.send(mention_string, embed=Embed(
                title=event.passcode_post_title,
                description=event.main_passcode_text))


