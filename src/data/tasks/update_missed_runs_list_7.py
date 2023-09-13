import bot
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_UpdateMissedRunsList(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.UPDATE_MISSED_RUNS_LIST

    @classmethod
    async def execute(cl, obj: object) -> None:
        if obj and obj["guild"] and obj["event_category"]:
            await bot.instance.data.ui.missed_runs_list.rebuild(obj["guild"], obj["event_category"])

