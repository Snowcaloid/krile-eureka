

from typing import override
from data_providers.tasks import TasksProvider
from data_writers._base import BaseWriter
from models.context import ExecutionContext
from models.task import TaskStruct

#TODO: Finish implementation of TasksWriter
class TasksWriter(BaseWriter[TaskStruct]):
    @override
    def provider(self) -> TasksProvider: return TasksProvider()

    @override
    def _validate_input(self, context: ExecutionContext,
                        struct: TaskStruct,
                        old_struct: TaskStruct,
                        deleting: bool) -> None:
        if deleting:
            assert old_struct, f'struct <{struct}> does not exist and cannot be deleted.'
        ...