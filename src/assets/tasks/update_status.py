from datetime import datetime, timedelta
from typing import override

from discord import Activity, ActivityType, Status
from basic_types import TaskExecutionType
import bot
from data.db.sql import SQL
from data.events.event import Event
from data.events.event_category import EventCategory
from data.tasks.task import TaskTemplate


class Task_UpdateStatus(TaskTemplate):
    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.UPDATE_STATUS

    @override
    async def handle_exception(self, e: Exception, obj: object) -> None:
        self.tasks.remove_all(TaskExecutionType.UPDATE_STATUS)
        self.tasks.add_task(datetime.utcnow() + timedelta(minutes=1), TaskExecutionType.UPDATE_STATUS)

    @override
    def runtime_only(self) -> bool: return True

    @override
    async def execute(self, obj: object) -> None:
        next_exec = datetime.utcnow() + timedelta(minutes=1)
        try: # TODO: Isn't it more efficient to use the runtime data object?
            record = SQL('events').select(fields=['id'],
                                          where=('timestamp > (current_timestamp at time zone \'UTC\') '
                                                 'and (not canceled or canceled is null) and '
                                                 '(not finished or finished is null)'),
                                          sort_fields=[('timestamp')])
            if record:
                event = Event()
                event.load(record['id'])
                if event.time > datetime.utcnow():
                    delta: timedelta = event.time - datetime.utcnow()
                    if delta.days:
                        if delta.seconds // 3600:
                            desc = f'{str(delta.days)}d {str(delta.seconds // 3600)}h {str((delta.seconds % 3600) // 60)}m'
                        else:
                            desc = f'{str(delta.days)}d {str((delta.seconds % 3600) // 60)}m'
                    elif delta.seconds // 3600:
                        desc = f'{str(delta.seconds // 3600)}h {str((delta.seconds % 3600) // 60)}m'
                    else:
                        desc = f'{str((delta.seconds % 3600) // 60)}m'

                    event_description = event.description if event.category == EventCategory.CUSTOM else event.short_description
                    desc = f'{event_description} in {desc} ({bot.instance.get_guild(event.guild_id).name})'
                    await bot.instance.change_presence(activity=Activity(type=ActivityType.playing, name=desc), status=Status.online)
            else:
                await bot.instance.change_presence(activity=None, status=None)
        finally:
            self.tasks.remove_all(TaskExecutionType.UPDATE_STATUS)
            self.tasks.add_task(next_exec, TaskExecutionType.UPDATE_STATUS)


