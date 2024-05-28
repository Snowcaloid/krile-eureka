from datetime import datetime
import bot
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction
from typing import Optional
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.tasks.tasks import TaskExecutionType
from data.validation.input_validator import InputValidator
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message

###################################################################################
# schedule
###################################################################################
class ScheduleCommands(GroupCog, group_name='schedule', group_description='Commands regarding scheduling runs.'):
    @command(name = "add", description = "Add an entry to the schedule.")
    @check(PermissionValidator.is_raid_leader)
    async def add(self, interaction: Interaction, event_type: str,
                  event_date: str, event_time: str,
                  description: Optional[str] = '',
                  auto_passcode: Optional[bool] = True,
                  use_support: Optional[bool] = True):
        await default_defer(interaction, False)
        event_type = InputValidator.NORMAL.event_type_name_to_type(event_type)
        if not await InputValidator.RAISING.check_valid_event_type(interaction, event_type): return
        if not await InputValidator.RAISING.check_valid_raid_leader(interaction, interaction.user, event_type): return
        if not await InputValidator.RAISING.check_custom_run_has_description(interaction, event_type, description): return
        event_datetime = await InputValidator.RAISING.check_and_combine_date_and_time(interaction, event_date, event_time)
        if not event_datetime: return
        schedule = bot.instance.data.guilds.get(interaction.guild_id).schedule
        event = schedule.add(interaction.user.id, event_type, event_datetime, description, auto_passcode, use_support)
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        if event.use_pl_posts:
            await bot.instance.data.ui.pl_post.create(interaction.guild_id, event.id)
        guild = bot.instance.data.guilds.get(interaction.guild_id)
        if guild:
            notification_channel = guild.channels.get(GuildChannelFunction.RUN_NOTIFICATION, event_type)
            if notification_channel:
                channel = interaction.guild.get_channel(notification_channel.id)
                mentions = await guild.pings.get_mention_string(GuildPingType.RUN_NOTIFICATION, event.type)
                await channel.send(f'{mentions} {await event.to_string()} has been scheduled.')
        event.create_tasks()
        await default_response(interaction, f'The run #{str(event.id)} has been scheduled.')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has scheduled a {event_type} run #{event.id} for {event_time}.')

    @command(name = "cancel", description = "Cancel a schedule entry.")
    @check(PermissionValidator.is_raid_leader)
    async def cancel(self, interaction: Interaction, event_id: int):
        await default_defer(interaction, False)
        if not await InputValidator.RAISING.check_run_exists(interaction, event_id): return
        if not await InputValidator.RAISING.check_allowed_to_change_run(interaction, event_id): return
        bot.instance.data.guilds.get(interaction.guild_id).schedule.cancel(event_id)
        await bot.instance.data.ui.pl_post.remove(interaction.guild_id, event_id)
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        await default_response(interaction, f'Run #{event_id} has been canceled.')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has canceled the run #{event_id}.')

    @command(name = "edit", description = "Edit an entry from the schedule.")
    @check(PermissionValidator.is_raid_leader)
    async def edit(self, interaction: Interaction, event_id: int, event_type: Optional[str] = None,
                   raid_leader: Optional[str] = None, event_date: Optional[str] = None,
                   event_time: Optional[str] = None, description: Optional[str] = None,
                   auto_passcode: Optional[bool] = None, use_support: Optional[bool] = None):
        await default_defer(interaction, False)
        if not await InputValidator.RAISING.check_run_exists(interaction, event_id): return
        schedule = bot.instance.data.guilds.get(interaction.guild_id).schedule
        event = schedule.get(event_id)
        check_type = event.type if event_type is None else event_type
        if event_type:
            event_type = InputValidator.NORMAL.event_type_name_to_type(event_type)
            check_type = event_type
        if not await InputValidator.RAISING.check_valid_event_type(interaction, check_type): return
        if not await InputValidator.RAISING.check_valid_raid_leader(interaction, interaction.user, check_type): return
        event_datetime = await InputValidator.RAISING.check_and_combine_date_and_time_change_for_event(interaction, event_id, event_date, event_time)
        if not event_datetime: return
        if use_support is None: use_support = event.use_support
        is_type_change = event_type and event_type != event.type
        is_passcode_change = not auto_passcode is None and event.auto_passcode != auto_passcode
        is_time_change = event.time != event_datetime
        if is_type_change:
            await bot.instance.data.ui.pl_post.remove(interaction.guild_id, event_id)
        event = schedule.edit(event_id, raid_leader, event_type, event_datetime,
                              InputValidator.NORMAL.escape_event_description(description), auto_passcode, use_support)
        if is_type_change:
            await bot.instance.data.ui.pl_post.create(interaction.guild_id, event_id)
        if is_time_change or is_passcode_change:
            event.recreate_tasks()
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        await bot.instance.data.ui.pl_post.rebuild(interaction.guild_id, event_id, True)
        await default_response(interaction, f'The run #{str(event_id)} has been adjusted.')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has adjusted run #{str(event_id)}')

    @add.autocomplete('event_type')
    @edit.autocomplete('event_type')
    async def autocomplete_schedule_type(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_type(interaction, current)

    @edit.autocomplete('raid_leader')
    async def autocomplete_leader(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.raid_leader(interaction, current)

    @add.autocomplete('event_date')
    @edit.autocomplete('event_date')
    async def autocomplete_schedule_date(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.date(current)

    @add.autocomplete('event_time')
    @edit.autocomplete('event_time')
    async def autocomplete_schedule_time(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.time(current)

    #region error-handling
    @add.error
    @cancel.error
    @edit.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion
