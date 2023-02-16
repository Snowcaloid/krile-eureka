from dotenv import load_dotenv
# Load all environment variables before doing anything else
load_dotenv()

import os
from datetime import datetime
from bot import snowcaloid
from views import PersistentView
from buttons import ButtonType, RoleSelectionButton, PartyLeaderButton
from data.table.tasks import TaskExecutionType
import commands
import tasks

# Is there a way to import a unit, without it showing up as unused in VSCode?
commands.so_that_import_works()

# Restore all Button functionality
async def recreate_view(bot): # Can't type this to Snowcaloid because of circular reference error
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
        if ButtonType.ROLE_POST.value in buttondata.button_id:
            view.add_item(RoleSelectionButton(label=buttondata.label, custom_id=buttondata.button_id))
        elif ButtonType.PL_POST.value in buttondata.button_id:
            view.add_item(PartyLeaderButton(label=buttondata.label, custom_id=buttondata.button_id))
    return views

# What the bot does upon connecting to discord
@snowcaloid.event
async def on_ready():
    await snowcaloid.data.load_db_data()
    snowcaloid.data.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS) 
    await snowcaloid.tree.sync()
    print(f'{snowcaloid.user} has connected to Discord!')
    if not tasks.task_loop.is_running():
        tasks.task_loop.start()

# Set the procedure for recreating button functionality, then run the bot
snowcaloid.recreate_view = recreate_view
snowcaloid.run(os.getenv('DISCORD_TOKEN'))
