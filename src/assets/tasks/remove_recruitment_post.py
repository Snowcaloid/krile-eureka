from datetime import datetime
from typing import override

from data_providers.channel_assignments import ChannelAssignmentProvider
from data_providers.events import EventsProvider
from models.channel_assignment import ChannelAssignmentStruct
from models.event import EventStruct
from utils.basic_types import ChannelDenominator, ChannelFunction, TaskExecutionType
from tasks.task import TaskTemplate


class Task_RemoveRecruitmentPost(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_RECRUITMENT_POST

    @override
    def description(self, data: dict, timestamp: datetime) -> str:
        return f'Remove Recruitment Post at {timestamp.strftime("%Y-%m %H:%M ST")}'

    @override
    async def execute(self, obj: dict) -> None:
        if obj and obj["guild"] and obj["message_id"]:
            event_struct = EventsProvider().find(EventStruct(
                guild_id=obj["guild"],
                recruitment_post_id=obj["message_id"]
            ))
            if not event_struct: return
            channel_assignment_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
                guild_id=event_struct.guild_id,
                function=ChannelFunction.RECRUITMENT,
                denominator=ChannelDenominator.EVENT_TYPE,
                event_type=event_struct.event_type
            ))
            if not channel_assignment_struct: return
            message = await self.bot.get_text_channel(channel_assignment_struct.channel_id).fetch_message(event_struct.recruitment_post_id)
            if message is None: return
            await message.delete()


