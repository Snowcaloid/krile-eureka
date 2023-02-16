import os

from dotenv import load_dotenv
from bot import snowcaloid
from views import PersistentView
from buttons import ButtonType, RoleSelectionButton, PartyLeaderButton
import commands
import tasks

load_dotenv()

commands.so_that_import_works()

TOKEN = os.getenv('DISCORD_TOKEN')

async def recreate_view(bot):
    bot.data.load_db_view()
    views = []
    i = 0
    view = PersistentView()
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

@snowcaloid.event
async def on_ready():
    await snowcaloid.data.load_db_data()
    await snowcaloid.tree.sync()
    print(f'{snowcaloid.user} has connected to Discord!')
    if not tasks.refresh_bot_status.is_running():
        tasks.refresh_bot_status.start()
    if not tasks.send_pl_passcodes.is_running():
        tasks.send_pl_passcodes.start()
    if not tasks.remove_old_runs.is_running():
        tasks.remove_old_runs.start()
    if not tasks.remove_old_pl_posts.is_running():
        tasks.remove_old_pl_posts.start()

snowcaloid.recreate_view = recreate_view
snowcaloid.run(TOKEN)
