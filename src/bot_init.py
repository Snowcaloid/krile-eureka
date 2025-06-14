
from datetime import datetime
from os import getenv
from typing import Literal, Optional
from centralized_data import Singleton
from discord.ext import tasks
from discord import HTTPException, Member, Object, RawMessageDeleteEvent
from discord.ext.commands import Bot, guild_only, Context, Greedy

# TODO: webserver - from api_server import ApiServer
from ui.base_button import delete_buttons
from utils.basic_types import TaskExecutionType
from bot import Bot
from data.cache.message_cache import MessageCache
from tasks import Tasks
from utils.logger import guild_log_message

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

async def setup_hook(client: Bot):
    await client.add_cog(EmbedCommands())
    await client.add_cog(ScheduleCommands())
    await client.add_cog(LogCommands())
    await client.add_cog(PingCommands())
    await client.add_cog(ConfigCommands())
    await client.add_cog(CopyCommands())
    await client.add_cog(EurekaCommands())
    await client.add_cog(BACommands())
    await client.add_cog(LogosCommands())
    await client.add_cog(AdminCommands())
    if not task_loop.is_running():
        task_loop.start()


def _load_singleton(singleton: Singleton, initial: bool = False):
    if not initial: # Constructor of all my data classes calls load() anyway
        singleton.load()

from data.events.schedule import Schedule
from services.channel_assignments import ChannelAssignmentsService
from data.guilds.guild_messages import GuildMessages
from ui.button_loader import ButtonLoader
from data.eureka_info import EurekaInfo
from ui.ui_schedule import UISchedule

async def reload_hook(client: Bot, initial: bool):
    ui_schedule = UISchedule()
    MessageCache().clear()
    await ButtonLoader().load()
    _load_singleton(EurekaInfo(), initial)
    for guild in client.guilds:
        _load_singleton(Schedule(guild.id), initial)
        _load_singleton(ChannelAssignmentsService(guild.id), initial)
        _load_singleton(GuildMessages(guild.id), initial)
        await ui_schedule.rebuild(guild.id)

    tasks = Tasks()
    _load_singleton(tasks, initial)

    if not tasks.contains(TaskExecutionType.UPDATE_STATUS):
        tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_STATUS)
    if not tasks.contains(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS):
        tasks.add_task(datetime.utcnow(), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)

client = Bot()._client

# What the bot does upon connecting to discord for the first time
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.reload_data_classes(True) #
    for guild in client.guilds:
        from utils.logger import guild_log_message
        message = (
            f'{client.user.mention} has successfully started.\n'
        )
        await guild_log_message(guild.id, message)

    # TODO: webserver - ApiServer().start()

@client.event
async def on_member_join(member: Member):
    await guild_log_message(member.guild.id, f'{member.mention} joined the server.')

@client.event
async def on_raw_message_delete(payload: RawMessageDeleteEvent):
    delete_buttons(payload.message_id)
    message_cache = MessageCache()
    if await message_cache.get(payload.message_id, None) is None: return
    message_cache.remove(payload.message_id)

@client.command()
@guild_only()
async def sync(ctx: Context, guilds: Greedy[Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if ctx.author.id != int(getenv('OWNER_ID')) and not ctx.author.guild_permissions.administrator: return
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
        tasks = Tasks()
        task = tasks.get_next()
        if task is None: return
        if tasks.executing: return
        tasks.executing = True
        try:
            await task.execute()
        finally:
            tasks.remove_task(task)
            tasks.executing = False

client.krile_setup_hook = setup_hook
client.krile_reload_hook = reload_hook