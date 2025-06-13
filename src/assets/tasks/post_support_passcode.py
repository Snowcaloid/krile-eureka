from datetime import datetime
from typing import override
from discord import Embed
from models.channel import ChannelStruct
from models.roles import RoleStruct
from providers.channels import ChannelsProvider
from providers.roles import RolesProvider
from utils.basic_types import GuildChannelFunction, GuildRoleFunction, TaskExecutionType
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
            channel_struct = ChannelsProvider().find(ChannelStruct(
                guild_id=obj["guild"],
                event_type=event.type,
                function=GuildChannelFunction.SUPPORT_PASSCODES
            ))
            if channel_struct is None: return
            guild = self._bot.client.get_guild(obj["guild"])
            channel = guild.get_channel(channel_struct.channel_id)
            if channel is None: return
            mention_string = RolesProvider().as_discord_mention_string(RoleStruct(
                guild_id=guild.id,
                event_type=event.type,
                function=GuildRoleFunction.SUPPORT_PASSCODE_PING
            ))
            await channel.send(mention_string, embed=Embed(
                title=event.passcode_post_title,
                description=event.support_passcode_text))


