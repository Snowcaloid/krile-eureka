from __future__ import annotations
from json import dumps
from typing import List, override
from datetime import datetime

from data.db.sql import SQL, Record
from data.tasks.task import Task, TaskExecutionType, TaskTemplate
from register import AssetLoader

class Tasks(AssetLoader[Task]):
    _list: List[Task] = []
    _runtime_tasks: List[Task] = []
    executing: bool = False

    def task_template(self, type: TaskExecutionType) -> TaskTemplate:
        return next(task for task in self.loaded_assets if task.type() == type)

    @override
    def asset_folder_name(self): return 'tasks'

    def load(self):
        self._list.clear()
        for record in SQL('tasks').select(fields=['id'],
                                          all=True,
                                          sort_fields=['execution_time']):
            task = Task(self.loaded_assets)
            task.load(record['id'])
            self._list.append(task)

    def sort_runtime_tasks_by_time(self) -> None:
        self._runtime_tasks = sorted(self._runtime_tasks, key=lambda task: task.time)

    def add_task(self, time: datetime, task_type: TaskExecutionType, data: object = None) -> None:
        if self.task_template(task_type).runtime_only():
            task = Task(self.loaded_assets)
            task.time = time
            task.data = data
            task.template = self.task_template(task_type)
            self._runtime_tasks.append(task)
            self.sort_runtime_tasks_by_time()
        else:
            SQL('tasks').insert(Record(execution_time=time, task_type=task_type.value, data=dumps(data), description=task_type.name))
            self.load()

    def contains(self, type: TaskExecutionType) -> bool:
        for task in self._list:
            if task.type == type:
                return True
        return False

    def get_next(self) -> Task:
        """Gets the next possible task to be executed."""
        task1, task2 = None, None
        if self._list and self._list[0].time <= datetime.utcnow():
            task1 = self._list[0]
        if self._runtime_tasks and self._runtime_tasks[0].time <= datetime.utcnow():
            task2 = self._runtime_tasks[0]

        if task1 and task2:
            if task1.time < task2.time:
                return task1
            else:
                return task2
        elif task1:
            return task1
        elif task2:
            return task2

        return None

    def remove_task(self, task: Task):
        if task.runtime_only:
            if task in self._runtime_tasks:
                self._runtime_tasks.remove(task)
        else:
            SQL('tasks').delete(f'id={task.id}')
            self.load()

    def remove_all(self, type: TaskExecutionType):
        if self.task_template(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type, self._runtime_tasks))
        else:
            SQL('tasks').delete(f'task_type={type.value}')
            self.load()

    def remove_task_by_data(self, type: TaskExecutionType, data: object):
        if data is None:
            return

        if self.task_template(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type and task.data == data, self._runtime_tasks))
        else:
            SQL('tasks').delete(f'task_type={type.value} and data=\'{dumps(data)}\'')
            self.load()
