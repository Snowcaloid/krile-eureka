from __future__ import annotations
from typing import Any, List
from datetime import datetime

from utils.basic_types import TaskExecutionType
from data.db.sql import SQL
from centralized_data import PythonAsset
from abc import abstractmethod

from utils.logger import guild_log_message

class TaskTemplate(PythonAsset):
    @abstractmethod
    def base_asset_class_name(self) -> str: return 'TaskTemplate'

    @abstractmethod
    def type(self) -> TaskExecutionType: return TaskExecutionType.NONE

    async def handle_exception(self, e: Exception, obj: dict) -> None:
        if obj.get("guild"):
            await guild_log_message(obj["guild"], e)
        else:
            print(e)

    @abstractmethod
    def runtime_only(self) -> bool: return False

    @abstractmethod
    def description(self, data: dict, timestamp: datetime) -> str: ...

    @abstractmethod
    async def execute(self, data: dict) -> None: pass


class Task:
    template: TaskTemplate
    id: int
    time: datetime
    data: dict
    signature: Any
    _task_templates: List[TaskTemplate]

    def __init__(self, task_templates: List[TaskTemplate]) -> None:
        self._task_templates = task_templates

    def load(self, id: int) -> None:
        record = SQL('tasks').select(fields=['execution_time', 'data', 'task_type'],
                                     where=f'id={id}')
        if record:
            self.id = id
            self.time = record['execution_time']
            self.data = record['data']
            self.template = next(task for task in self._task_templates if task.type() == TaskExecutionType(record['task_type']))

    @property
    def type(self) -> TaskExecutionType:
        return self.template.type()

    @property
    def runtime_only(self) -> bool:
        return self.template.runtime_only()

    async def execute(self) -> None:
        try:
            await self.template.execute(self.data)
        except Exception as e:
            await self.template.handle_exception(e, self.data)
