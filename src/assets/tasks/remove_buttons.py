from data.tasks.task import TaskExecutionType, TaskTemplate
from data.ui.buttons import delete_buttons


class Task_RemoveButtons(TaskTemplate):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.REMOVE_BUTTONS

    @classmethod
    async def execute(cl, obj: object) -> None:
        if obj and obj["message_id"]:
            message_id = obj["message_id"]
            delete_buttons(message_id)


