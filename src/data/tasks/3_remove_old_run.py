import bot
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_RemoveOldRun(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_RUNS

    @classmethod
    async def execute(cl, obj: object) -> None:
        if obj and obj["id"]:
            for guild in bot.instance.data.guilds.all:
                guild.schedule.finish(obj["id"])
                await bot.instance.data.ui.schedule.rebuild(guild.id)


Task_RemoveOldRun.register()
