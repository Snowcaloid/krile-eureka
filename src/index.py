import asyncio
import debugpy

debugpy.listen(("0.0.0.0", 5678))

from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os

if os.getenv('WAIT_DEBUG').upper() == 'TRUE':
    print('Waiting for Debugger to attach.')
    debugpy.wait_for_client()

import bot

# What the bot does upon connecting to discord for the first time
@bot.instance.event
async def on_ready():
    print(f'{bot.instance.user} has connected to Discord!')
    while not bot.instance.data.ready:
        print('Waiting for data to be ready...')
        await asyncio.sleep(500)
    from data.guilds.guild import Guilds
    for guild in Guilds().all:
        from logger import guild_log_message
        message = (
            f'{bot.instance.user.mention} has successfully started.\n'
        )
        await guild_log_message(guild.id, message)


bot.instance.run(os.getenv('DISCORD_TOKEN'))
