from typing import override
import bot
from data.guilds.guild import Guilds
from data.tasks.task import TaskExecutionType, TaskTemplate


class Task_RemoveOldRun(TaskTemplate):
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_RUNS

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["id"]:
            for guild in self.guilds.all:
                guild.schedule.finish(obj["id"])
                await bot.instance.data.ui.schedule.rebuild(guild.id)


