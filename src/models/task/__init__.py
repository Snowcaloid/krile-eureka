

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

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(TaskType, self.task_type)
        assert isinstance(fixed_enum, TaskType), f"invalid task type: {fixed_enum}"
        self.task_type = fixed_enum
