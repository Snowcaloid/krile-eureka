from typing import override
from basic_types import TaskExecutionType
import bot
from data.tasks.task import TaskTemplate


class Task_RemoveOldRun(TaskTemplate):
    from data.guilds.guild import Guilds
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    from data.events.schedule import Schedule
    @Schedule.bind
    def schedule(self) -> Schedule: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_RUNS

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["id"]:
            self.schedule.finish(obj["id"])
            for guild in self.guilds.all:
                await bot.instance.data.ui.schedule.rebuild(guild.id)


