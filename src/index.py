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

from data.db.definition import TableDefinitions

# initialize all tables before anything else is done
# this way the order of loading of any global data class is irrelevant
TableDefinitions()

import bot

# What the bot does upon connecting to discord for the first time
@bot.instance.event
async def on_ready():
    print(f'{bot.instance.user} has connected to Discord!')
    for guild in bot.instance.guilds:
        from logger import guild_log_message
        message = (
            f'{bot.instance.user.mention} has successfully started.\n'
        )
        await guild_log_message(guild.id, message)

bot.instance.run(os.getenv('DISCORD_TOKEN'))
