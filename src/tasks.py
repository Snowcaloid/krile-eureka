import bot
import data.message_cache as cache
from datetime import datetime, timedelta
from discord.ext import tasks
from discord import Activity, ActivityType, Embed, Status

from data.table.schedule import ScheduleType, schedule_type_desc
from data.table.tasks import TaskExecutionType
from utils import set_default_footer

@tasks.loop(seconds=1) # The delay is calculated from the end of execution of the last task.
async def task_loop(): # You can think of it as sleep(1000) after the last procedure finished
    """Main loop, which runs required tasks at required times. await is necessery."""
    if bot.krile.data.ready and bot.krile.ws:
        task = bot.krile.data.tasks.get_next()
        if task:
            if task.task_type == TaskExecutionType.UPDATE_STATUS:
                await refresh_bot_status()
            elif task.task_type == TaskExecutionType.SEND_PL_PASSCODES:
                await send_pl_passcodes(task.data)
            elif task.task_type == TaskExecutionType.REMOVE_OLD_RUNS:
                await remove_old_run(task.data)
            elif task.task_type == TaskExecutionType.REMOVE_OLD_PL_POSTS:
                await remove_old_pl_post(task.data)
            elif task.task_type == TaskExecutionType.POST_MAIN_PASSCODE:
                await post_main_passcode(task.data)
            elif task.task_type == TaskExecutionType.POST_SUPPORT_PASSCODE:
                await post_support_passcode(task.data)
            elif task.task_type == TaskExecutionType.REMOVE_MISSED_RUN_POST:
                await remove_missed_run_post(task.data)

            bot.krile.data.tasks.remove_task(task.id)

async def refresh_bot_status():
    """Changes bot's status to <Playing Run type in [time until next run]>, or empties it."""
    next_exec = datetime.utcnow() + timedelta(minutes=1)
    bot.krile.data.db.connect()
    try:
        q = bot.krile.data.db.query('select type, timestamp from schedule where not canceled and not finished order by timestamp limit 1')
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
            await bot.krile.change_presence(activity=Activity(type=ActivityType.playing, name=desc), status=Status.online)
        else:
            await bot.krile.change_presence(activity=None, status=None)
    finally:
        bot.krile.data.tasks.remove_all(TaskExecutionType.UPDATE_STATUS)
        bot.krile.data.db.disconnect()
        bot.krile.data.tasks.add_task(next_exec, TaskExecutionType.UPDATE_STATUS)

async def remove_old_run(data: object):
    """Removes run <id> from runtime data and the database."""
    if data and data["id"]:
        for post in bot.krile.data.schedule_posts._list:
            post.remove(data["id"])
            await post.update_post()

async def remove_old_pl_post(data: object):
    """Removes Party leader recruitment post."""
    if data and data["guild"] and data["channel"]:
        guild = bot.krile.get_guild(data["guild"])
        channel = guild.get_channel(data["channel"])
        async for message in channel.history(limit=50):
            if len(message.content.split('#')) == 2:
                id = int(message.content.split('#')[1])
                if not bot.krile.data.schedule_posts.get_post(guild.id).contains(id):
                    await message.delete()

async def send_pl_passcodes(data: object):
    """Sends all allocated party leaders and the raid leader the passcodes for the run."""
    if data and data["guild"] and data["entry_id"]:
        entry = bot.krile.data.schedule_posts.get_post(data["guild"]).get_entry(data["entry_id"])
        if entry:
            guild = bot.krile.get_guild(data["guild"])
            member = guild.get_member(entry.leader)
            use_support = False
            if entry.type.startswith('BA'):
                parties = ['1', '2', '3', '4', '5', '6']
                use_support = True
            elif entry.type.startswith('DRS'):
                parties = ['A', 'B', 'C', 'D', 'E', 'F']
            support = f'Support passcode: {str(int(entry.pass_supp)).zfill(4)}' if use_support else ''
            await member.send((
                'Raid Leader notification:\n'
                f'Main party passcode: {str(int(entry.pass_main)).zfill(4)}\n{support}'
            ))
            for user in entry.party_leaders:
                if user and user != entry.leader and user != entry.party_leaders[6]:
                    member = guild.get_member(user)
                    await member.send((
                        'Party Leader notification:\n'
                        f'You are party {parties[entry.party_leaders.index(user)]}.\n'
                        f'The main party passcode is {str(int(entry.pass_main)).zfill(4)}'
                    ))
            if entry.party_leaders[6]:
                member = guild.get_member(entry.party_leaders[6])
                await member.send((
                    'Party Leader notification:\n'
                    'You are support party.'
                    f'The support passcode is {str(int(entry.pass_supp)).zfill(4)}'
                ))

async def post_main_passcode(data: object):
    """Sends the main party passcode embed to the allocated passcode channel."""
    if data and data["guild"] and data["entry_id"]:
        entry = bot.krile.data.schedule_posts.get_post(data["guild"]).get_entry(data["entry_id"])
        if entry:
            guild_data = bot.krile.data.guild_data.get_data(data["guild"])
            if entry and guild_data:
                channel_data = guild_data.get_channel(type=entry.type)
                if channel_data:
                    guild = bot.krile.get_guild(data["guild"])
                    channel = guild.get_channel(channel_data.channel_id)
                    if channel:
                        rl = guild.get_member(entry.leader)
                        desc = schedule_type_desc(entry.type) if entry.type != ScheduleType.CUSTOM.value else entry.description
                        description = (
                            f'Raid Leader: {rl.mention}\n\n'
                            f'**The passcode for main parties is going to be: {str(int(entry.pass_main)).zfill(4)}**\n'
                        )
                        if entry.type.startswith('BA'):
                            description += (
                            'This passcode will not work for support parties.\n\n'
                            '*Do not forget to bring __Spirit of Remembered__ and proper actions.*'
                        )
                        embed=Embed(
                            title=entry.timestamp.strftime('%A, %d %B %Y %H:%M ') + desc + "\nPasscode",
                            description=description)
                        message = await channel.send(embed=embed)
                        await set_default_footer(message)

async def post_support_passcode(data: object):
    """Sends the support party passcode embed to the allocated passcode channel."""
    if data and data["guild"] and data["entry_id"]:
        entry = bot.krile.data.schedule_posts.get_post(data["guild"]).get_entry(data["entry_id"])
        if entry:
            guild_data = bot.krile.data.guild_data.get_data(data["guild"])
            if entry and guild_data:
                channel_data = guild_data.get_support_channel(type=entry.type)
                if channel_data:
                    guild = bot.krile.get_guild(data["guild"])
                    channel = guild.get_channel(channel_data.channel_id)
                    if channel:
                        rl = guild.get_member(entry.leader)
                        desc = schedule_type_desc(entry.type) if entry.type != ScheduleType.CUSTOM.value else entry.description
                        embed=Embed(
                            title=entry.timestamp.strftime('%A, %d %B %Y %H:%M ') + desc + "\nPasscode",
                            description=(
                                f'Raid Leader: {rl.mention}\n\n'
                                f'**The passcode for the SUPPORT party is going to be: {str(int(entry.pass_supp)).zfill(4)}**\n'
                                'This passcode will not work for main (1-6) parties.\n\n'
                                '*Do not forget to bring __Spirit of Remembered__ and proper actions.*\n'
                                'Support needs to bring dispel for the NM Ovni.'
                            ))
                        message = await channel.send(embed=embed)
                        await set_default_footer(message)

async def remove_missed_run_post(data: object):
    """Removes a missed run post."""
    if data and data["guild"] and data["channel"] and data["message"]:
        guild = bot.krile.get_guild(data["guild"])
        if guild:
            channel = guild.get_channel(data["channel"])
            if channel:
                message = await cache.messages.get(data["message"], channel)
                if message:
                    await message.delete()