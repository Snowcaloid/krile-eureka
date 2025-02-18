from __future__ import annotations
from typing import List
from datetime import datetime

from data.db.sql import SQL
from register import LoadedAsset
from abc import abstractmethod
from enum import Enum

from logger import guild_log_message

class TaskExecutionType(Enum):
    NONE = 0
    UPDATE_STATUS = 1
    SEND_PL_PASSCODES = 2
    REMOVE_OLD_RUNS = 3
    REMOVE_OLD_MESSAGE = 4
    POST_MAIN_PASSCODE = 5
    POST_SUPPORT_PASSCODE = 6
    REMOVE_BUTTONS = 8
    UPDATE_EUREKA_INFO_POSTS = 9

class TaskTemplate(LoadedAsset):
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
