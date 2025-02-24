from typing import override

from centralized_data import Singleton
from basic_types import TaskExecutionType
from discord.ext.commands import Bot
from data.events.schedule import Schedule
from data.tasks.task import TaskTemplate


class Task_RemoveOldRun(TaskTemplate):
    from data.ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_RUNS

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["id"]:
            Schedule().finish(obj["id"])
            for guild in Singleton.get_instance(Bot).guilds:
                await self.ui_schedule.rebuild(guild.id)


