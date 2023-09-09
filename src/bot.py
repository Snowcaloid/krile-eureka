from discord import Intents, Member, Object, HTTPException
from discord.ext.commands import Bot, guild_only, is_owner, Context, Greedy
from commands.config import ConfigCommands
from commands.ping import PingCommands
from data.runtime_data import RuntimeData
from data.tasks.tasks import TaskExecutionType
from commands.embed import EmbedCommands
from commands.schedule import ScheduleCommands
from commands.missed import MissedCommands
from commands.log import LogCommands
from datetime import datetime
from data.ui.views import PersistentView
from data.ui.buttons import ButtonType, RoleSelectionButton, PartyLeaderButton
from typing import Literal, Optional
from logger import guild_log_message
from discord.ext import tasks


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

    async def setup_hook(self) -> None:
        """A coroutine to be called to setup the bot.
        This method is called after instance.on_ready event.
        """
        await self.data.reset()
        if not self.data.tasks.contains(TaskExecutionType.UPDATE_STATUS):
            self.data.tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)

        await self.add_cog(EmbedCommands())
        await self.add_cog(MissedCommands())
        await self.add_cog(ScheduleCommands())
        await self.add_cog(LogCommands())
        await self.add_cog(PingCommands())
        await self.add_cog(ConfigCommands())
        if not task_loop.is_running():
            task_loop.start()


instance = Krile()

@tasks.loop(seconds=1) # The delay is calculated from the end of execution of the last task.
async def task_loop(): # You can think of it as sleep(1000) after the last procedure finished
    """Main loop, which runs required tasks at required times. await is necessery."""
    if instance.data.ready and instance.ws:
        task = instance.data.tasks.get_next()
        if task is None: return
        try:
            await task.execute()
        finally:
            instance.data.tasks.remove_task(task)

@instance.event
async def on_member_join(member: Member):
    await guild_log_message(member.guild.id, f'{member.mention} joined the server.')

@instance.command()
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

