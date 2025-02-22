from typing import override
from basic_types import TaskExecutionType
from data.tasks.task import TaskTemplate
from data.ui.buttons import delete_buttons


class Task_RemoveButtons(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_BUTTONS

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["message_id"]:
            message_id = obj["message_id"]
            delete_buttons(message_id)


