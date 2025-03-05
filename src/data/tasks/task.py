from __future__ import annotations
from typing import Any, List
from datetime import datetime

from utils.basic_types import TaskExecutionType
from data.db.sql import SQL
from centralized_data import PythonAsset
from abc import abstractmethod

from utils.logger import guild_log_message

class TaskTemplate(PythonAsset):
    @classmethod
    def base_asset_class_name(cls) -> str: return 'TaskTemplate'

    def type(cl) -> TaskExecutionType: return TaskExecutionType.NONE

    async def handle_exception(cl, e: Exception, obj: object) -> None:
        if obj["guild"]:
            await guild_log_message(obj["guild"], e)
        else:
            raise e

    def runtime_only(cl) -> bool: return False

    @abstractmethod
    async def execute(cl, obj: object) -> None: pass


class Task:
    template: TaskTemplate
    id: int
    time: datetime
    data: object
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
