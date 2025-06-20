

from typing import override
from data_providers.tasks import TasksProvider
from data_writers._base import BaseWriter
from models.context import ExecutionContext
from models.task import TaskStruct

#TODO: Finish implementation of TasksWriter
class TasksWriter(BaseWriter[TaskStruct]):
    def _validate_input(self, context, struct: TaskStruct, exists: bool, deleting: bool) -> None:
        if deleting:
            assert exists, f'struct <{struct}> does not exist and cannot be deleted.'
        ...

    @override
    def sync(self, struct: TaskStruct, context: ExecutionContext) -> None:
        with context:
            self._validate_input(context, struct, exists=False, deleting=False)
            ...

    @override
    def remove(self, struct: TaskStruct, context: ExecutionContext) -> None:
        with context:
            found_struct = TasksProvider().find(struct)
            self._validate_input(context, struct, exists=True, deleting=True)
            ...