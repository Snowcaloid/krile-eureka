from abc import abstractclassmethod
from enum import Enum
from json import dumps, loads
from typing import List, Type
import bot
from datetime import datetime
from data.db.database import pg_timestamp

from logger import guild_log_message


class TaskExecutionType(Enum):
    NONE = 0
    UPDATE_STATUS = 1
    SEND_PL_PASSCODES = 2
    REMOVE_OLD_RUNS = 3
    REMOVE_OLD_MESSAGE = 4
    POST_MAIN_PASSCODE = 5
    POST_SUPPORT_PASSCODE = 6
    UPDATE_MISSED_RUNS_LIST = 7
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
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select execution_time, data, task_type from tasks where id={id}')
            if record:
                self.id = id
                self.time = record[0][0]
                self.data = loads(record[0][1])
                for task_base in TaskBase._registered_tasks:
                    if task_base.type().value == record[0][2]:
                        self.base = task_base
                        break
        finally:
            db.disconnect()

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
        db = bot.instance.data.db
        db.connect()
        try:
            self._list.clear()
            records = db.query('select id from tasks order by execution_time')
            for record in records:
                task = Task(self)
                task.load(record[0])
                self._list.append(task)
        finally:
            db.disconnect()

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
            db = bot.instance.data.db
            db.connect()
            try:
                db.query(f'insert into tasks (execution_time, task_type, data) values ({pg_timestamp(time)}, {task_type.value}, \'{dumps(data)}\') returning id')
                self.load()
            finally:
                db.disconnect()

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
            db = bot.instance.data.db
            db.connect()
            try:
                db.query(f'delete from tasks where id={task.id}')
                self.load()
            finally:
                db.disconnect()

    def remove_all(self, type: TaskExecutionType):
        if TaskBase.by_type(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type, self._runtime_tasks))
        else:
            db = bot.instance.data.db
            db.connect()
            try:
                db.query(f'delete from tasks where task_type={type.value}')
                self.load()
            finally:
                db.disconnect()

    def remove_task_by_data(self, type: TaskExecutionType, data: object):
        if data is None:
            return

        if TaskBase.by_type(type).runtime_only():
            self._runtime_tasks = list(filter(lambda task: task.type != type and task.data == data, self._runtime_tasks))
        else:
            db = bot.instance.data.db
            db.connect()
            try:
                db.query(f'delete from tasks where task_type={type.value} and data=\'{dumps(data)}\'')
                self.load()
            finally:
                db.disconnect()
