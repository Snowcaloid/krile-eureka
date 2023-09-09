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
    REMOVE_OLD_PL_POSTS = 4
    POST_MAIN_PASSCODE = 5
    POST_SUPPORT_PASSCODE = 6
    REMOVE_MISSED_RUN_POST = 7


class TaskBase:
    _registered_tasks: List[Type['TaskBase']] = []

    @classmethod
    def register(cl) -> None:
        TaskBase._registered_tasks.append(cl)

    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.NONE
    @classmethod
    def handle_exception(cl, e: Exception, obj: object) -> None:
        if obj["guild"]:
            guild_log_message(obj["guild"], e)
        else:
            raise e

    @abstractclassmethod
    async def execute(cl, obj: object) -> None: pass


class Task:
    base: Type[TaskBase]
    id: int
    time: datetime
    data: object

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select execution_time, data, task_type from tasks where id={id}')
            if record:
                self.id = id
                self.time = record[0]
                self.data = loads(record[1])
                for type in TaskBase._registered_tasks:
                    if type.type().value == record[2]:
                        self.base = type
                        break
        finally:
            db.disconnect()

    @property
    def type(self) -> TaskExecutionType:
        return self.base.type()

    async def execute(self) -> None:
        try:
            await self.base.execute(self.data)
        except Exception as e:
            self.base.handle_exception(e, self.data)

class Tasks:
    _list: List[Task] = []

    def load(self):
        db = bot.instance.data.db
        db.connect()
        try:
            self._list.clear()
            records = db.query('select id from tasks order by execution_time')
            for record in records:
                task = Task()
                task.load(record[0])
                self._list.append(task)
        finally:
            db.disconnect()

    def add_task(self, time: datetime, type: TaskExecutionType, data: object = None) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'insert into tasks (execution_time, task_type, data) values ({pg_timestamp(time)}, {type.value}, \'{dumps(data)}\') returning id')
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
        if self._list and self._list[0].time <= datetime.utcnow():
            return self._list[0]
        return None

    def remove_task(self, id: int):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from tasks where id={id}')
            self.load()
        finally:
            db.disconnect()

    def remove_all(self, type: TaskExecutionType):
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

        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from tasks where task_type={type.value} and data=\'{dumps(data)}\'')
            self.load()
        finally:
            db.disconnect()
