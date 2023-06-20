from discord import Intents, Object, HTTPException
from discord.ext.commands import Bot, guild_only, is_owner, Context, Greedy
from commands.ping import PingCommands
from data.runtime_data import RuntimeData
from data.table.tasks import TaskExecutionType
from commands.embed import EmbedCommands
from commands.schedule import ScheduleCommands
from commands.missed import MissedCommands
from commands.log import LogCommands
from datetime import datetime
from views import PersistentView
from buttons import ButtonType, RoleSelectionButton, PartyLeaderButton
from typing import Literal, Optional
import tasks


class Krile(Bot):
    """General bot class.

    Properties
    ----------
    data: :class:`RuntimeData`
        This is where all the data is stored during runtime.
        The objects stored within this object have the access to the database.
    recreate_view: :class:`coroutine`
        It is called for restoring Button functionality within setup_hook procedure.
        To recreate the button's functionality, a view is needed to be added to the
        bot, which includes Buttons with previously existing custom_id's.
    """
    data: RuntimeData

    def __init__(self):
        intents = Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)
        self.data = RuntimeData()

    def recreate_view(self):
        self.data.load_db_view()
        views = []
        i = 0
        view = PersistentView()
        views.append(view)
        for buttondata in self.data._loaded_view:
            i += 1
            if i % 20 == 0:
                view = PersistentView()
                views.append(view)
            if ButtonType.ROLE_SELECTION.value in buttondata.button_id:
                view.add_item(RoleSelectionButton(label=buttondata.label, custom_id=buttondata.button_id))
            elif ButtonType.PL_POST.value in buttondata.button_id:
                view.add_item(PartyLeaderButton(label=buttondata.label, custom_id=buttondata.button_id))
        return views

    async def setup_hook(self) -> None:
        """A coroutine to be called to setup the bot.
        This method is called after snowcaloid.on_ready event.
        """
        await self.data.load_db_data()
        if not self.data.tasks.empty():
            self.data.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)

        await self.add_cog(EmbedCommands())
        await self.add_cog(MissedCommands())
        await self.add_cog(ScheduleCommands())
        await self.add_cog(LogCommands())
        await self.add_cog(PingCommands())
        await self.tree.sync()
        if not tasks.task_loop.is_running():
            tasks.task_loop.start()
        for view in self.recreate_view():
            self.add_view(view)


krile = Krile()

@krile.command()
@guild_only()
@is_owner()
async def sync(ctx: Context, guilds: Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

