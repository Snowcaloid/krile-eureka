from typing import override
from utils.basic_types import TaskExecutionType
from data.tasks.task import TaskTemplate
from ui.base_button import delete_buttons


class Task_RemoveButtons(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_BUTTONS

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["message_id"]:
            message_id = obj["message_id"]
            delete_buttons(message_id)


