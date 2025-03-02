import os

from discord.ext import tasks
from centralized_data import Singleton
from api_server import ApiServer
from data.cache.message_cache import MessageCache
from discord import Intents, Member, Object, HTTPException, RawMessageDeleteEvent
from discord.ext.commands import Bot, guild_only, Context, Greedy
from data.tasks.task import TaskExecutionType
from datetime import datetime
from typing import Literal, Optional
from data.tasks.tasks import Tasks
from logger import guild_log_message

class Krile(Bot, Singleton):
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
    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    def __init__(self):
        intents = Intents.all()
        intents.message_content = True
        intents.emojis = True
        intents.emojis_and_stickers = True
        intents.members = True
        super().__init__(command_prefix='/', intents=intents)

    def _load_singleton(self, singleton: Singleton, initial: bool = False):
        if not initial: # Constructor of all my data classes calls load() anyway
            singleton.load()

    async def reload_data_classes(self, initial: bool = False):
        from data.events.schedule import Schedule
        from data.guilds.guild_channel import GuildChannels
        from data.guilds.guild_messages import GuildMessages
        from data.guilds.guild_pings import GuildPings
        from data.guilds.guild_roles import GuildRoles
        from data.ui.button_loader import ButtonLoader
        from data.eureka_info import EurekaInfo
        from data.ui.ui_schedule import UISchedule

        ui_schedule = UISchedule()
        MessageCache().clear()
        self._load_singleton(ButtonLoader(), initial)
        self._load_singleton(EurekaInfo(), initial)
        for guild in self.guilds:
            self._load_singleton(Schedule(guild.id), initial)
            self._load_singleton(GuildChannels(guild.id), initial)
            self._load_singleton(GuildMessages(guild.id), initial)
            self._load_singleton(GuildRoles(guild.id), initial)
            self._load_singleton(GuildPings(guild.id), initial)
            await ui_schedule.rebuild(guild.id)

        tasks = Tasks()
        self._load_singleton(tasks, initial)

        if not tasks.contains(TaskExecutionType.UPDATE_STATUS):
            tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
        if not tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
            tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)

    async def setup_hook(self) -> None:
        """A coroutine to be called to setup the bot.
        This method is called after instance.on_ready event.
        """
        from commands.admin import AdminCommands
        from commands.ba import BACommands
        from commands.config import ConfigCommands
        from commands.copy import CopyCommands
        from commands.eureka import EurekaCommands
        from commands.logos import LogosCommands
        from commands.ping import PingCommands
        from commands.embed import EmbedCommands
        from commands.schedule import ScheduleCommands
        from commands.log import LogCommands
        await self.add_cog(EmbedCommands())
        await self.add_cog(ScheduleCommands())
        await self.add_cog(LogCommands())
        await self.add_cog(PingCommands())
        await self.add_cog(ConfigCommands())
        await self.add_cog(CopyCommands())
        await self.add_cog(EurekaCommands())
        await self.add_cog(BACommands())
        await self.add_cog(LogosCommands())
        await self.add_cog(AdminCommands())
        if not task_loop.is_running():
            task_loop.start()

client = Krile()

# What the bot does upon connecting to discord for the first time
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.reload_data_classes(True)
    for guild in client.guilds:
        from logger import guild_log_message
        message = (
            f'{client.user.mention} has successfully started.\n'
        )
        await guild_log_message(guild.id, message)

    ApiServer().start()

@client.event
async def on_member_join(member: Member):
    await guild_log_message(member.guild.id, f'{member.mention} joined the server.')

@client.event
async def on_raw_message_delete(payload: RawMessageDeleteEvent):
    client.tasks.add_task(datetime.utcnow(), TaskExecutionType.REMOVE_BUTTONS, {"message_id": payload.message_id})
    message_cache = MessageCache()
    if await message_cache.get(payload.message_id, None) is None: return
    message_cache.remove(payload.message_id)

@client.command()
@guild_only()
async def sync(ctx: Context, guilds: Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if ctx.author.id != int(os.getenv('OWNER_ID')) and not ctx.author.guild_permissions.administrator: return
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

@tasks.loop(seconds=1) # The delay is calculated from the end of execution of the last task.
async def task_loop(): # You can think of it as sleep(1000) after the last procedure finished
    """Main loop, which runs required tasks at required times. await is necessery."""
    if client.ws:
        task = client.tasks.get_next()
        if task is None: return
        if client.tasks.executing: return
        client.tasks.executing = True
        try:
            await task.execute()
        finally:
            client.tasks.remove_task(task)
            client.tasks.executing = False