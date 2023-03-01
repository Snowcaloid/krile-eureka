from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os
import bot
from datetime import datetime
from views import PersistentView
from buttons import ButtonType, RoleSelectionButton, PartyLeaderButton
from data.table.tasks import TaskExecutionType
from commands.embed import EmbedCommands
from commands.schedule import ScheduleCommands
from commands.missed import MissedCommands
from commands.log import LogCommands
import tasks

unload_commands = False

# Restore all Button functionality
async def recreate_view(bot: bot.Snowcaloid):
    bot.data.load_db_view()
    views = []
    i = 0
    view = PersistentView()
    views.append(view)
    for buttondata in bot.data._loaded_view:
        i += 1
        if i % 20 == 0:
            view = PersistentView()
            views.append(view)
        if ButtonType.ROLE_SELECTION.value in buttondata.button_id:
            view.add_item(RoleSelectionButton(label=buttondata.label, custom_id=buttondata.button_id))
        elif ButtonType.PL_POST.value in buttondata.button_id:
            view.add_item(PartyLeaderButton(label=buttondata.label, custom_id=buttondata.button_id))
    return views

# What the bot does upon connecting to discord
@bot.snowcaloid.event
async def on_ready():
    await bot.snowcaloid.data.load_db_data()
    bot.snowcaloid.data.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
    if not unload_commands:
        await bot.snowcaloid.add_cog(EmbedCommands())
        await bot.snowcaloid.add_cog(MissedCommands())
        await bot.snowcaloid.add_cog(ScheduleCommands())
        await bot.snowcaloid.add_cog(LogCommands())
    await bot.snowcaloid.tree.sync()
    print(f'{bot.snowcaloid.user} has connected to Discord!')
    if not tasks.task_loop.is_running():
        tasks.task_loop.start()

# Set the procedure for recreating button functionality, then run the bot
bot.snowcaloid.recreate_view = recreate_view
bot.snowcaloid.run(os.getenv('DISCORD_TOKEN'))
