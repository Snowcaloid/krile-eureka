from abc import abstractclassmethod
from enum import Enum
from json import dumps, loads
from typing import List, Type
from datetime import datetime

from data.db.sql import SQL, Record
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

class TaskBase:
    _registered_tasks: List[Type['TaskBase']] = []

    @classmethod
    def register(cl) -> None:
        TaskBase._registered_tasks.append(cl)

    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.NONE
    @classmethod
    async def handle_exception(cl, e: Exception, obj: object) -> None:
        if obj["guild"]:
            await guild_log_message(obj["guild"], e)
        else:
            raise e

    @classmethod
    def runtime_only(cl) -> bool: return False

    @abstractclassmethod
    async def internal_execute(cl, obj: object) -> None: pass

    @classmethod
    def by_type(cl, task_type: TaskExecutionType) -> Type['TaskBase']:
        return next(taskbase for taskbase in TaskBase._registered_tasks if taskbase.type() == task_type)


class Task:
    base: Type[TaskBase]
    id: int
    time: datetime
    data: object
    list: Type['Tasks']

    def __init__(self, list: Type['Tasks']) -> None:
        self.list = list

    def load(self, id: int) -> None:
        record = SQL('tasks').select(fields=['execution_time', 'data', 'task_type'],
                                     where=f'id={id}')
        if record:
            self.id = id
            self.time = record['execution_time']
            self.data = loads(record['data'])
            for task_base in TaskBase._registered_tasks:
                if task_base.type().value == record['task_type']:
                    self.base = task_base
                    break

    @property
    def type(self) -> TaskExecutionType:
        return self.base.type()

    @property
    def runtime_only(self) -> bool:
        return self.base.runtime_only()

    async def execute(self) -> None:
        self.list.executing = True
        try:
            await self.base.execute(self.data)
        except Exception as e:
            await self.base.handle_exception(e, self.data)
        finally:
            self.list.executing = False

class Tasks:
    _list: List[Task] = []
    _runtime_tasks: List[Task] = []
    executing: bool = False

    def load(self):
        self._list.clear()
        for record in SQL('tasks').select(fields=['id'],
                                          all=True,
                                          sort_fields=['execution_time']):
            task = Task(self)
            task.load(record['id'])
            self._list.append(task)

    def sort_runtime_tasks_by_time(self) -> None:
        self._runtime_tasks = sorted(self._runtime_tasks, key=lambda task: task.time)

    def add_task(self, time: datetime, task_type: TaskExecutionType, data: object = None) -> None:
        if TaskBase.by_type(task_type).runtime_only():
            task = Task(self)
            task.time = time
            task.data = data
            for task_base in TaskBase._registered_tasks:
                if task_base.type() == task_type:
                    task.base = task_base
                    break
            self._runtime_tasks.append(task)
            self.sort_runtime_tasks_by_time()
        else:
            SQL('tasks').insert(Record(execution_time=time, task_type=task_type.value, data=dumps(data)))
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
        if TaskBase.by_type(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type, self._runtime_tasks))
        else:
            SQL('tasks').delete(f'task_type={type.value}')
            self.load()

    def remove_task_by_data(self, type: TaskExecutionType, data: object):
        if data is None:
            return

        if TaskBase.by_type(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type and task.data == data, self._runtime_tasks))
        else:
            SQL('tasks').delete(f'task_type={type.value} and data=\'{dumps(data)}\'')
            self.load()
