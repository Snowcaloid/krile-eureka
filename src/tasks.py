from datetime import datetime, timedelta
from bot import snowcaloid
from discord.ext import tasks
from discord import Activity, ActivityType, Status

from data.table.schedule import schedule_type_desc

@tasks.loop(minutes=1)
async def refresh_bot_status():
    if snowcaloid.data.ready:
        snowcaloid.data.db.connect()
        try:
            q = snowcaloid.data.db.query('select type, timestamp from schedule order by timestamp limit 1')
            if q:
                now = datetime.utcnow()
                delta: timedelta = q[0][1] - now
                desc = schedule_type_desc(q[0][0]) + ' in '
                need_comma = delta.days
                if delta.days:
                    desc += str(delta.days) + ' days'
                if delta.seconds // 60:
                    if need_comma:
                        desc += ', '
                    desc += f'{str(delta.seconds // 3600)} hours, {str((delta.seconds % 3600) // 60)} minutes'
                await snowcaloid.change_presence(activity=Activity(type=ActivityType.playing, name=desc), status=Status.online)
        finally:
            snowcaloid.data.db.disconnect()