from datetime import datetime, timedelta

from discord import Activity, ActivityType, Status
import bot
from data.db.sql import SQL
from data.events.event import ScheduledEvent
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_UpdateStatus(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.UPDATE_STATUS
    @classmethod
    async def handle_exception(cl, e: Exception, obj: object) -> None:
        bot.instance.data.tasks.remove_all(TaskExecutionType.UPDATE_STATUS)
        bot.instance.data.tasks.add_task(datetime.utcnow() + timedelta(minutes=1), TaskExecutionType.UPDATE_STATUS)

    @classmethod
    def runtime_only(cl) -> bool: return True

    @classmethod
    async def execute(cl, obj: object) -> None:
        next_exec = datetime.utcnow() + timedelta(minutes=1)
        try: # TODO: Isn't it more efficient to use the runtime data object?
            record = SQL('events').select(fields=['id'],
                                          where=('timestamp > (current_timestamp at time zone \'UTC\') '
                                                 'and (not canceled or canceled is null) and '
                                                 '(not finished or finished is null)'),
                                          sort_fields=[('timestamp')])
            if record:
                event = ScheduledEvent()
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
                    desc = f'{event.short_description} in {desc}'
                    await bot.instance.change_presence(activity=Activity(type=ActivityType.playing, name=desc), status=Status.online)
            else:
                await bot.instance.change_presence(activity=None, status=None)
        finally:
            bot.instance.data.tasks.remove_all(TaskExecutionType.UPDATE_STATUS)
            bot.instance.data.tasks.add_task(next_exec, TaskExecutionType.UPDATE_STATUS)


