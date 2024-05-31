from data.tasks.tasks import TaskExecutionType, TaskBase
from data.ui.buttons import delete_buttons


class Task_RemoveButtons(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.REMOVE_BUTTONS

    @classmethod
    async def execute(cl, obj: object) -> None:
        if obj and obj["message_id"]:
            message_id = obj["message_id"]
            delete_buttons(message_id)


