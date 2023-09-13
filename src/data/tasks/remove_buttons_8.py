import bot
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_RemoveButtons(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.REMOVE_BUTTONS

    @classmethod
    async def execute(cl, obj: object) -> None:
        if obj and obj["message_id"]:
            db = bot.instance.data.db
            db.connect()
            try:
                message_id = obj["message_id"]
                db.query(f'delete from buttons where message_id=\'{message_id}\'')
            finally:
                db.disconnect()


