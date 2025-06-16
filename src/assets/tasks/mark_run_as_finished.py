from typing import override

from utils.basic_types import TaskExecutionType
from data.events.schedule import Schedule
from tasks.task import TaskTemplate


class Task_MarkRunAsFinished(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from ui.schedule import SchedulePost
    @SchedulePost.bind
    def ui_schedule(self) -> SchedulePost: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.MARK_RUN_AS_FINISHED

    @override
    async def execute(self, obj: dict) -> None:
        if obj and obj["id"]:
            Schedule(obj["guild"]).finish(obj["id"])
            for guild in self.bot._client.guilds:
                await self.ui_schedule.rebuild(guild.id)


