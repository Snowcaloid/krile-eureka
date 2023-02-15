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

@tasks.loop(minutes=2)
async def remove_old_runs():
    if snowcaloid.data.ready:
        snowcaloid.data.db.connect()
        try:
            for post in snowcaloid.data.schedule_posts._list:
                for entry in post._list:
                    if entry.timestamp < datetime.utcnow():
                        post.remove(entry.id)
            snowcaloid.data.db.query(f'delete from schedule where timestamp < now() at time zone \'utc\'')
        finally:
            snowcaloid.data.db.disconnect()
            
@tasks.loop(hours=12)
async def remove_old_pl_posts():
    if snowcaloid.data.ready:
        for data in snowcaloid.data.guild_data._list:
            guild = snowcaloid.get_guild(data.guild_id)
            for channel_data in data._channels:
                if channel_data.is_pl_channel:
                    channel = await guild.fetch_channel(channel_data.channel_id)
                    async for message in channel.history(limit=50):
                        if len(message.content.split('#')) == 2:
                            id = int(message.content.split('#')[1])
                            if not snowcaloid.data.schedule_posts.get_post(guild.id).contains(id):
                                await message.delete()
                
@tasks.loop(seconds=20)
async def send_pl_passcodes():
    if snowcaloid.data.ready:
        for post in snowcaloid.data.schedule_posts._list:
            for entry in post._list:
                if not entry.notified and entry.timestamp - timedelta(hours=1) <= datetime.utcnow():
                    guild = snowcaloid.get_guild(post.guild)
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
                    entry.notified = True
        