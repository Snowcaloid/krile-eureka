from discord.ext import tasks
import debugpy

debugpy.listen(("0.0.0.0", 5678))

from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os

if os.getenv('WAIT_DEBUG').upper() == 'TRUE':
    print('Waiting for Debugger to attach.')
    debugpy.wait_for_client()

from data.db.definition import TableDefinitions

# initialize all tables before anything else is done
# this way the order of loading of any global data class is irrelevant
TableDefinitions()

import bot

client = bot.Krile()

@tasks.loop(seconds=1) # The delay is calculated from the end of execution of the last task.
async def task_loop(): # You can think of it as sleep(1000) after the last procedure finished
    """Main loop, which runs required tasks at required times. await is necessery."""
    if client.ws:
        task = client.tasks.get_next()
        if task is None: return
        if client.tasks.executing: return
        client.tasks.executing = True
        try:
            await task.execute()
        finally:
            client.tasks.remove_task(task)
            client.tasks.executing = False

# What the bot does upon connecting to discord for the first time
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.reload_data_classes(True)
    if not task_loop.is_running():
        task_loop.start()
    for guild in client.guilds:
        from logger import guild_log_message
        message = (
            f'{client.user.mention} has successfully started.\n'
        )
        await guild_log_message(guild.id, message)

client.run(os.getenv('DISCORD_TOKEN'))
