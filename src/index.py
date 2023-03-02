from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os
import bot

# What the bot does upon connecting to discord for the first time
@bot.snowcaloid.event
async def on_ready():
    print(f'{bot.snowcaloid.user} has connected to Discord!')

bot.snowcaloid.run(os.getenv('DISCORD_TOKEN'))
