import bot
import data.cache.message_cache as cache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction, Embed
from discord.channel import TextChannel
from typing import Optional
from data.events.event import Event, EventCategory
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.validation.input_validator import InputValidator
from utils import filter_choices_by_current, set_default_footer, default_defer, default_response
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message

###################################################################################
# schedule
###################################################################################
class ScheduleCommands(GroupCog, group_name='schedule', group_description='Commands regarding scheduling runs.'):
    @command(name = "initialize", description = "Initialize the server\'s schedule by creating a static post that will be used as a schedule list.")
    @check(PermissionValidator.is_admin)
    async def initialize(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        schedule = bot.instance.data.guilds.get(interaction.guild_id).schedule
        if schedule.schedule_post.id:
            message = await cache.messages.get(schedule.schedule_post.id, schedule.schedule_post.channel)
            if message:
                await message.delete()
        message = await channel.send(embed=Embed())
        await set_default_footer(message)
        bot.instance.data.guilds.get(interaction.guild_id).schedule.schedule_post.set(message.id, channel.id)
        bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        await default_response(interaction, f'Schedule has been created in #{channel.name}')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has created a schedule post in #{channel.name}.')

    @command(name = "add", description = "Add an entry to the schedule.")
    @check(PermissionValidator.is_raid_leader)
    async def add(self, interaction: Interaction, event_type: str,
                  event_date: str, event_time: str,
                  description: Optional[str] = '',
                  auto_passcode: Optional[bool] = True):
        await default_defer(interaction, False)
        if not await InputValidator.RAISING.check_valid_event_type(interaction, event_type): return
        if not await InputValidator.RAISING.check_valid_raid_leader(interaction, interaction.user, event_type): return
        if not await InputValidator.RAISING.check_custom_run_has_description(interaction, event_type, description): return
        event_datetime = await InputValidator.RAISING.check_and_combine_date_and_time(interaction, event_date, event_time)
        if not event_datetime: return
        schedule = bot.instance.data.guilds.get(interaction.guild_id).schedule
        event = schedule.add(interaction.user.id, event_type, event_datetime, description, auto_passcode)
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        if event.use_pl_posts:
            await bot.instance.data.ui.pl_post.create(interaction.guild_id, event.id)
        await default_response(interaction, f'The run #{str(event.id)} has been scheduled.')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has scheduled a {event_type} run #{event.id} for {event_time}.')

    @command(name = "cancel", description = "Cancel a schedule entry.")
    @check(PermissionValidator.is_raid_leader)
    async def cancel(self, interaction: Interaction, event_id: int):
        await default_defer(interaction, False)
        if not await InputValidator.RAISING.check_run_exists(interaction, event_id): return
        if not await InputValidator.RAISING.check_allowed_to_change_run(interaction, event_id): return
        bot.instance.data.guilds.get(interaction.guild_id).schedule.cancel(event_id)
        await default_response(interaction, f'Run #{event_id} has been cenceled.')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has canceled the run #{event_id}.')

    @command(name = "edit", description = "Edit an entry from the schedule.")
    @check(PermissionValidator.is_raid_leader)
    async def edit(self, interaction: Interaction, event_id: int, event_type: Optional[str] = None,
                   raid_leader: Optional[str] = None, event_date: Optional[str] = None,
                   event_time: Optional[str] = None, description: Optional[str] = None,
                   auto_passcode: Optional[bool] = None):
        await default_defer(interaction, False)
        if not await InputValidator.RAISING.check_run_exists(interaction, event_id): return
        schedule = bot.instance.data.guilds.get(interaction.guild_id).schedule
        event = schedule.get(event_id)
        check_type = event.type if event_type is None else event_type
        if not await InputValidator.RAISING.check_valid_event_type(interaction, check_type): return
        if not await InputValidator.RAISING.check_valid_raid_leader(interaction, interaction.user, check_type): return
        event_datetime = await InputValidator.RAISING.check_and_combine_date_and_time_change_for_event(interaction, event_id, event_date, event_time)
        if not event_datetime: return
        schedule.edit(event_id, raid_leader, event_type, event_datetime,
                      InputValidator.NORMAL.escape_event_description(description), auto_passcode)
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        await bot.instance.data.ui.pl_post.rebuild(interaction.guild_id, event_id)
        await default_response(interaction, f'The run #{str(event_id)} has been adjusted.')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has adjusted run #{str(event_id)}')

    async def config_channel(self, interaction: Interaction, event_type: str, channel: TextChannel,
                             function: GuildChannelFunction, function_desc: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        channels_data = bot.instance.data.guilds.get(interaction.guild_id).channels
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            channels_data.set(channel.id, function, event_type)
            desc = Event.by_type(event_type).short_description()
        else:
            channels_data.set_category(channel.id, function, EventCategory(event_type))
            desc = EventCategory(event_type).value
        await default_response(interaction, f'You have set #{channel.name} as the {function_desc} channel for type "{desc}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has set #{channel.name} as the {function_desc} channel for type "{Event.by_type(event_type).short_description()}".')

    @command(name = "passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted.")
    @check(PermissionValidator.is_admin)
    async def passcode_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.PASSCODES, 'main passcode')

    @command(name = "support_passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted (for support parties).")
    @check(PermissionValidator.is_admin)
    async def support_passcode_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.SUPPORT_PASSCODES, 'support passcode')

    @command(name = "party_leader_channel", description = "Set the channel for party leader posts.")
    @check(PermissionValidator.is_admin)
    async def party_leader_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.PL_CHANNEL, 'party leader recruitment')

    @add.autocomplete('event_type')
    @edit.autocomplete('event_type')
    #@filter_choices_by_current
    async def autocomplete_schedule_type(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_type(interaction)

    @passcode_channel.autocomplete('event_type')
    @party_leader_channel.autocomplete('event_type')
    @support_passcode_channel.autocomplete('event_type')
    #@filter_choices_by_current
    async def autocomplete_schedule_type_with_all(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_type_with_categories()

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
    @initialize.error
    @add.error
    @cancel.error
    @edit.error
    @passcode_channel.error
    @support_passcode_channel.error
    @party_leader_channel.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion
