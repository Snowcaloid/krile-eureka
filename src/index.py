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
    for guild in bot.instance.data.guilds.all:
        from logger import guild_log_message
        from asset_loader import AssetLoader
        message = (
            f'{bot.instance.user.mention} has successfully started.\n'
            'Launch messages:\n'
        )
        await guild_log_message(guild.id, message)
        launch_messages = AssetLoader._log.splitlines(True)
        limit = 2000 - 20 # leeway for the code block
        message = ''
        for line in launch_messages:
            limit -= len(line)
            if limit <= 0:
                await guild_log_message(guild.id, f'```\n{message}```\n')
                message = line
                limit = 2000 - 20 - len(line)
            else:
                message += line
        if message:
            await guild_log_message(guild.id, f'```\n{message}```\n')


bot.instance.run(os.getenv('DISCORD_TOKEN'))
