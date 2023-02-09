import os

from dotenv import load_dotenv
from bot import snowcaloid
import commands

commands.so_that_import_works()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

@snowcaloid.event
async def on_ready():
    await snowcaloid.tree.sync()
    print(f'{snowcaloid.user} has connected to Discord!')

snowcaloid.run(TOKEN)
