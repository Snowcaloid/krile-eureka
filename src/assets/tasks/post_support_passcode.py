from datetime import datetime
from typing import override
from discord import Embed, Guild, TextChannel
from models.channel_assignment import ChannelAssignmentStruct
from models.roles import RoleStruct
from providers.channel_assignments import ChannelAssignmentProvider
from providers.roles import RolesProvider
from utils.basic_types import GuildChannelFunction, RoleFunction, TaskExecutionType
from data.events.schedule import Schedule
from tasks.task import TaskTemplate


class Task_PostSupportPasscode(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.POST_SUPPORT_PASSCODE

    @override
    def description(self, data: dict, timestamp: datetime) -> str:
        return f'Post Support Passcode for event {data["entry_id"]} at {timestamp.strftime("%Y-%m %H:%M ST")}'

    @override
    async def execute(self, obj: dict) -> None:
        """Sends the support party passcode embed to the allocated passcode channel."""
        if obj and obj["guild"] and obj["entry_id"]:
            event = Schedule(obj["guild"]).get(obj["entry_id"])
            if event is None: return
            channel_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
                guild_id=obj["guild"],
                event_type=event.type,
                function=GuildChannelFunction.SUPPORT_PASSCODES
            ))
            if channel_struct is None: return
            guild = self._bot._client.get_guild(obj["guild"])
            if not isinstance(guild, Guild): return
            channel = guild.get_channel(channel_struct.channel_id)
            if not isinstance(channel, TextChannel): return
            mention_string = RolesProvider().as_discord_mention_string(RoleStruct(
                guild_id=guild.id,
                event_category=event.type,
                function=RoleFunction.SUPPORT_PASSCODE_PING
            ))
            await channel.send(mention_string, embed=Embed(
                title=event.passcode_post_title,
                description=event.support_passcode_text))


