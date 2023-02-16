from datetime import datetime, timedelta
from bot import snowcaloid
from discord.ext import tasks
from discord import Activity, ActivityType, Status

from data.table.schedule import schedule_type_desc
from data.table.tasks import TaskExecutionType

@tasks.loop(seconds=1) # The delay is calculated from the end of execution of the last task.
async def task_loop(): # You can think of it as sleep(1000) after the last procedure finished
    if snowcaloid.data.ready:
        task = snowcaloid.data.tasks.get_next()
        if task:
            if task.task_type == TaskExecutionType.UPDATE_STATUS:
                await refresh_bot_status()
            elif task.task_type == TaskExecutionType.SEND_PL_PASSCODES:
                await send_pl_passcodes(task.data)
            elif task.task_type == TaskExecutionType.REMOVE_OLD_RUNS:
                await remove_old_run(task.data)
            elif task.task_type == TaskExecutionType.REMOVE_OLD_PL_POSTS:
                await remove_old_pl_post(task.data)
            snowcaloid.data.tasks.remove_task(task.id)

async def refresh_bot_status():
    next_exec = datetime.utcnow() + timedelta(minutes=1)
    snowcaloid.data.db.connect()
    try:
        q = snowcaloid.data.db.query('select type, timestamp from schedule order by timestamp limit 1')
        if q and q[0][1] > datetime.utcnow():
            now = datetime.utcnow()
            delta: timedelta = q[0][1] - now
            desc = schedule_type_desc(q[0][0]) + ' in '
            need_comma = delta.days
            if delta.days:
                desc += str(delta.days) + ' days'
            if delta.seconds // 60:
                if need_comma:
                    desc += ', '
                desc += f' {str(delta.seconds // 3600)} hours, {str((delta.seconds % 3600) // 60)} minutes'
            await snowcaloid.change_presence(activity=Activity(type=ActivityType.playing, name=desc), status=Status.online)
        else:
            await snowcaloid.change_presence(activity=None, status=None)
    finally:
        snowcaloid.data.db.disconnect()
        snowcaloid.data.tasks.add_task(next_exec, TaskExecutionType.UPDATE_STATUS)

async def remove_old_run(data: object):
    if data and data["id"]:
        for post in snowcaloid.data.schedule_posts._list:
            post.remove(data["id"])
            
async def remove_old_pl_post(data: object):
    if data and data["guild"] and data["channel"]:
        guild = snowcaloid.get_guild(data["guild"])
        channel = await guild.fetch_channel(data["channel"])
        async for message in channel.history(limit=50):
            if len(message.content.split('#')) == 2:
                id = int(message.content.split('#')[1])
                if not snowcaloid.data.schedule_posts.get_post(guild.id).contains(id):
                    await message.delete()
                
async def send_pl_passcodes(data: object):
    if data and data["guild"] and data["entry_id"]:
        entry = snowcaloid.data.schedule_posts.get_post(data["guild"]).get_entry(data["entry_id"])
        guild = snowcaloid.get_guild(data["guild"])
        member = await guild.fetch_member(entry.owner)
        await member.send((
            'Raid Leader notification:\n'
            f'Main party passcode: {str(int(entry.pass_main)).zfill(4)}\n'
            f'Support passcode: {str(int(entry.pass_supp)).zfill(4)}'
        ))
        for user in entry.party_leaders:
            if user and user != entry.owner and user != entry.party_leaders[6]:
                member = await guild.fetch_member(user)
                await member.send((
                    'Party Leader notification:\n'
                    f'The main party passcode is {str(int(entry.pass_main)).zfill(4)}'
                ))
        if entry.party_leaders[6]:
            member = await guild.fetch_member(entry.party_leaders[6])
            await member.send((
                'Party Leader notification:\n'
                f'The support passcode is {str(int(entry.pass_supp)).zfill(4)}'
            ))
        