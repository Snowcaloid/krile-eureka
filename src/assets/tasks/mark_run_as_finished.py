from typing import override

from utils.basic_types import TaskExecutionType
from data.events.schedule import Schedule
from data.tasks.task import TaskTemplate


class Task_MarkRunAsFinished(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.MARK_RUN_AS_FINISHED

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["id"]:
            Schedule(obj["guild"]).finish(obj["id"])
            for guild in self.bot.client.guilds:
                await self.ui_schedule.rebuild(guild.id)


