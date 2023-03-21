from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os
import bot

# What the bot does upon connecting to discord for the first time
@bot.krile.event
async def on_ready():
    print(f'{bot.krile.user} has connected to Discord!')

bot.krile.run(os.getenv('DISCORD_TOKEN'))
