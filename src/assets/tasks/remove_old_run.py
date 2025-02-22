from typing import override
from basic_types import TaskExecutionType
import bot
from data.events.schedule import Schedule
from data.tasks.task import TaskTemplate


class Task_RemoveOldRun(TaskTemplate):
    from data.ui.ui import UI
    @UI.bind
    def ui(self) -> UI: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_RUNS

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["id"]:
            Schedule().finish(obj["id"])
            for guild in bot.instance.guilds:
                await self.ui.schedule.rebuild(guild.id)


