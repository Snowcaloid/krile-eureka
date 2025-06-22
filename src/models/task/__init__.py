
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import override
from models._base import BaseStruct
from utils.basic_types import TaskType
from utils.functions import fix_enum

@dataclass
class TaskStruct(BaseStruct):
    id: int = Unassigned #type: ignore
    execution_time: datetime = Unassigned #type: ignore
    task_type: TaskType = Unassigned #type: ignore
    data: dict = Unassigned #type: ignore

    @classmethod
    def db_table_name(cls) -> str: return 'tasks'

    @override
    def type_name(self) -> str: return 'task'

    @override
    def identity(self) -> TaskStruct:
        return TaskStruct(id=self.id)

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(TaskType, self.task_type)
        assert isinstance(fixed_enum, TaskType), f'invalid task type: {fixed_enum}'
        self.task_type = fixed_enum

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.id, int):
            result.append(f'ID: {self.id}')
        if isinstance(self.execution_time, datetime):
            result.append(f'Execution Time: {self.execution_time}')
        if isinstance(self.task_type, TaskType):
            result.append(f'Task Type: {self.task_type.name}')
        return f'Task({', '.join(result)})'

    @override
    def changes_since(self, other: TaskStruct) -> str:
        result = []
        if isinstance(self.id, int) and self.id != other.id:
            result.append(f'ID: {other.id} -> {self.id}')
        if isinstance(self.execution_time, datetime) and self.execution_time != other.execution_time:
            result.append(f'Execution Time: {other.execution_time} -> {self.execution_time}')
        if isinstance(self.task_type, TaskType) and self.task_type != other.task_type:
            result.append(f'Task Type: {other.task_type.name} -> {self.task_type.name}')

