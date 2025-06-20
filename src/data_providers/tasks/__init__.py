

from typing import Type, override
from data_providers._base import BaseProvider
from models.task import TaskStruct


class TasksProvider(BaseProvider[TaskStruct]):
    @override
    def struct_type(self) -> Type[TaskStruct]:
        return TaskStruct