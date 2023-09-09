from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os
import bot

from data.tasks.task_registers import TaskRegisters
TaskRegisters.register_all()

from data.events.event_register import EventRegister
EventRegister.register_all()

# What the bot does upon connecting to discord for the first time
@bot.instance.event
async def on_ready():
    print(f'{bot.instance.user} has connected to Discord!')

bot.instance.run(os.getenv('DISCORD_TOKEN'))
