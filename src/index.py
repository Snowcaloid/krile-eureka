import os

from dotenv import load_dotenv
from bot import snowcaloid
import commands
import tasks

commands.so_that_import_works()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

@snowcaloid.event
async def on_ready():
    await snowcaloid.data.load_db_data(snowcaloid)
    await snowcaloid.tree.sync()
    print(f'{snowcaloid.user} has connected to Discord!')
    if not tasks.refresh_bot_status.is_running():
        tasks.refresh_bot_status.start()

snowcaloid.run(TOKEN)
