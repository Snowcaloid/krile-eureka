from datetime import datetime
import time as mod_time
from json import dumps, loads
from typing import List
import bot
from data.table.database import pg_timestamp
from data.table.tasks import TaskData, TaskExecutionType

class TaskList:
    """Runtime data object containing tasks requiring execution.

    Properties
    ----------
    _list: :class:`List[TaskData]`
        List of tasks
    """
    _list: List[TaskData]

    def __init__(self) -> None:
        self._list = []

    def add_task(self, time: datetime, type: TaskExecutionType, data: object = None):
        """Adds task into the runtime task list and into the database.
        The internal list is then resorted.

        Args:
            time (datetime): Execution time for the task
            type (TaskExecutionType): Type of task to be executed
            data (object, optional): Miscellaneous data that can be passed to the task when it's executed (JSON). Defaults to None.

        Returns:
            None
        """
        taskdata = TaskData(time, type)
        taskdata.data = data
        self._list.append(taskdata)
        def sort(data: TaskData):
            dt = data.execution_time
            date_tuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            return int(mod_time.mktime(datetime(*date_tuple).timetuple()))
        self._list.sort(key=sort)
        bot.snowcaloid.data.db.connect()
        try:
            id = bot.snowcaloid.data.db.query(f'insert into tasks (execution_time, task_type, data) values ({pg_timestamp(time)}, {type.value}, \'{dumps(data)}\') returning id')
            taskdata.id = id
        finally:
            bot.snowcaloid.data.db.disconnect()

    def empty(self) -> bool:
        """Is the task list empty?"""
        return len(self._list) == 0

    def get_next(self) -> TaskData:
        """Gets the next possible task to be executed."""
        if not self.empty():
            if self._list[0].execution_time <= datetime.utcnow():
                return self._list[0]
        return None

    def remove_task(self, id: int):
        """Removes a task from the runtime object and the database.

        Args:
            id (int): Task id
        """
        for taskdata in self._list:
            if taskdata.id == id:
                self._list.remove(taskdata)
        bot.snowcaloid.data.db.connect()
        try:
            bot.snowcaloid.data.db.query(f'delete from tasks where id={id}')
        finally:
            bot.snowcaloid.data.db.disconnect()

    def remove_task_by_data(self, type: TaskExecutionType, data: object):
        """Removes a task from the runtime object and the database.

        Args:
            type (TaskExecutionType): Task type
            data (object): data equaling to what needs to be removed
        """
        for taskdata in self._list:
            if taskdata.task_type == type and dumps(taskdata.data) == dumps(data):
                self._list.remove(taskdata)
        bot.snowcaloid.data.db.connect()
        try:
            bot.snowcaloid.data.db.query(f'delete from tasks where task_type={type.value} and data=\'{dumps(data)}\'')
        finally:
            bot.snowcaloid.data.db.disconnect()

    def load(self):
        """Load the list of tasks from the database."""
        bot.snowcaloid.data.db.connect()
        try:
            q = bot.snowcaloid.data.db.query('select id, execution_time, task_type, data from tasks order by execution_time')
            for record in q:
                taskdata = TaskData(record[1], TaskExecutionType(record[2]))
                taskdata.id = record[0]
                if record[3]:
                    taskdata.data = loads(record[3])
                self._list.append(taskdata)
        finally:
            bot.snowcaloid.data.db.disconnect()