from __future__ import annotations
from asyncio import sleep
from json import dumps
from typing import Any, Callable, List, override
from datetime import datetime
from uuid import uuid4

from utils.basic_types import TaskExecutionType
from data.db.sql import _SQL, Record
from tasks.task import Task, TaskTemplate
from centralized_data import PythonAssetLoader

class Tasks(PythonAssetLoader[TaskTemplate]):
    @override
    def constructor(self) -> None:
        super().constructor()
        self._db_tasks: List[Task] = []
        self._runtime_tasks: List[Task] = []
        self.executing: bool = False
        self.load()

    def task_template(self, type: TaskExecutionType) -> TaskTemplate:
        return next(task for task in self.loaded_assets if task.type() == type)

    @override
    def asset_folder_name(self): return 'tasks'

    def load(self):
        self._db_tasks.clear()
        for record in _SQL('tasks').select(fields=['id'],
                                          all=True,
                                          sort_fields=['execution_time']):
            task = Task(self.loaded_assets)
            task.load(record['id'])
            task.signature = uuid4()
            self._db_tasks.append(task)

    def sort_runtime_tasks_by_time(self) -> None:
        self._runtime_tasks = sorted(self._runtime_tasks, key=lambda task: task.time)

    def add_task(self, time: datetime, task_type: TaskExecutionType, data: dict = None) -> Any:
        if self.task_template(task_type).runtime_only():
            task = Task(self.loaded_assets)
            task.time = time
            task.data = data
            task.signature = uuid4()
            task.template = self.task_template(task_type)
            self._runtime_tasks.append(task)
            self.sort_runtime_tasks_by_time()
            return task.signature
        else:
            _SQL('tasks').insert(Record(
                execution_time=time,
                task_type=task_type.value,
                data=dumps(data),
                description=self.task_template(task_type).description(data, time)
            ))
            self.load()

    def contains(self, type: TaskExecutionType) -> bool:
        for task in self._db_tasks:
            if task.type == type:
                return True
        return False

    def contains_signature(self, signature: Any) -> bool:
        for task in self._runtime_tasks:
            if task.signature == signature:
                return True
        for task in self._db_tasks:
            if task.signature == signature:
                return True
        return False

    async def until_over(self, signature: Any):
        while self.contains_signature(signature):
            await sleep(1)

    def get_next(self) -> Task:
        """Gets the next possible task to be executed."""
        task1, task2 = None, None
        if self._db_tasks and self._db_tasks[0].time <= datetime.utcnow():
            task1 = self._db_tasks[0]
        if self._runtime_tasks and self._runtime_tasks[0].time <= datetime.utcnow():
            task2 = self._runtime_tasks[0]

        if task1 and task2:
            if task1.time < task2.time:
                return task1
            else:
                return task2
        elif task1:
            return task1
        else:
            return task2

    def remove_task(self, task: Task):
        if task.runtime_only:
            if task in self._runtime_tasks:
                self._runtime_tasks.remove(task)
        else:
            _SQL('tasks').delete(f'id={task.id}')
            self.load()

    def remove_all(self, type: TaskExecutionType):
        if self.task_template(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type, self._runtime_tasks))
        else:
            _SQL('tasks').delete(f'task_type={type.value}')
            self.load()

    def remove_task_by_data(self, type: TaskExecutionType, data: dict):
        if data is None:
            return

        if self.task_template(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type and task.data == data, self._runtime_tasks))
        else:
            _SQL('tasks').delete(f'task_type={type.value} and data=\'{dumps(data)}\'')
            self.load()

    @classmethod
    def run_async_method(cls, method: Callable[...], *args, **kwargs) -> None:
        cls().add_task(datetime.utcnow(), TaskExecutionType.RUN_ASYNC_METHOD, {
            "method": method,
            "args": args,
            "kwargs": kwargs
        })
