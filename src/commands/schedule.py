import copy
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction
from typing import Optional
from data.events.schedule import Schedule
from data.generators.autocomplete_generator import AutoCompleteGenerator
from utils.basic_types import GuildChannelFunction
from utils.basic_types import GuildPingType
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from utils.functions import default_defer
from data.validation.permission_validator import PermissionValidator
from utils.logger import feedback_and_log, guild_log_message

###################################################################################
# schedule
###################################################################################
class ScheduleCommands(GroupCog, group_name='schedule', group_description='Commands regarding scheduling runs.'):
    from data.ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    from data.ui.ui_recruitment_post import UIRecruitmentPost
    @UIRecruitmentPost.bind
    def ui_recruitment_post(self) -> UIRecruitmentPost: ...

    from data.validation.user_input import UserInput
    @UserInput.bind
    def user_input(self) -> UserInput: ...

    @command(name = "add", description = "Add an entry to the schedule.")
    @check(PermissionValidator().is_raid_leader)
    async def add(self, interaction: Interaction, event_type: str,
                  event_date: str, event_time: str,
                  description: Optional[str] = '',
                  auto_passcode: Optional[bool] = True,
                  use_support: Optional[bool] = True):
        await default_defer(interaction, False)
        event_type = self.user_input.correction.event_type_name_to_type(event_type, interaction.guild_id)
        if await self.user_input.fail.is_not_event_type(interaction, event_type): return
        if await self.user_input.fail.is_not_raid_leader_for(interaction, interaction.user, event_type): return
        if await self.user_input.fail.is_custom_run_without_description(interaction, event_type, description): return
        if await self.user_input.fail.invalid_date_string_format(interaction, event_date): return
        if await self.user_input.fail.invalid_time_string_format(interaction, event_time): return
        event_datetime = self.user_input.correction.combine_date_and_time(event_date, event_time)
        if await self.user_input.fail.event_time_in_past(interaction, event_datetime): return
        if not event_datetime: return
        event = Schedule(interaction.guild_id).add(interaction.user.id, event_type, event_datetime, description, auto_passcode, use_support)
        await self.ui_schedule.rebuild(interaction.guild_id)
        if event.use_recruitment_posts:
            await self.ui_recruitment_post.create(interaction.guild_id, event.id)
        notification_channel = GuildChannels(interaction.guild_id).get(GuildChannelFunction.RUN_NOTIFICATION, event_type)
        if notification_channel:
            channel = interaction.guild.get_channel(notification_channel.id)
            mentions = await GuildPings(interaction.guild_id).get_mention_string(GuildPingType.RUN_NOTIFICATION, event.type)
            await channel.send(f'{mentions} {await event.to_string()} has been scheduled.')
        event.create_tasks()
        await feedback_and_log(interaction, f'scheduled a {event_type} run #{event.id} for {event_time} with description: <{event.description}>.')

    @command(name = "cancel", description = "Cancel a schedule entry.")
    @check(PermissionValidator().is_raid_leader)
    async def cancel(self, interaction: Interaction, event_id: int):
        await default_defer(interaction, False)
        if await self.user_input.fail.event_does_not_exist(interaction, event_id): return
        if await self.user_input.fail.cant_change_run(interaction, event_id): return
        Schedule(interaction.guild_id).cancel(event_id)
        await self.ui_recruitment_post.remove(interaction.guild_id, event_id)
        await self.ui_schedule.rebuild(interaction.guild_id)
        await feedback_and_log(interaction, f'canceled the run #{event_id}.')

    @command(name = "edit", description = "Edit an entry from the schedule.")
    @check(PermissionValidator().is_raid_leader)
    async def edit(self, interaction: Interaction, event_id: int, event_type: Optional[str] = None,
                   raid_leader: Optional[str] = None, event_date: Optional[str] = None,
                   event_time: Optional[str] = None, description: Optional[str] = None,
                   auto_passcode: Optional[bool] = None, use_support: Optional[bool] = None):
        await default_defer(interaction, False)
        if await self.user_input.fail.event_does_not_exist: return
        old_event = Schedule(interaction.guild_id).get(event_id)
        check_type = old_event.type if event_type is None else event_type
        if event_type:
            event_type = self.user_input.correction.event_type_name_to_type(event_type, interaction.guild_id)
            check_type = event_type
        if await self.user_input.fail.is_not_event_type(interaction, event_type): return
        if await self.user_input.fail.is_not_raid_leader_for(interaction, interaction.user, check_type): return
        raid_leader = self.user_input.correction.member_name_to_id(interaction.guild_id, raid_leader)
        event = Schedule(interaction.guild_id).get(event_id)
        if event_date:
            if await self.user_input.fail.invalid_date_string_format(interaction, event_date): return
        if event_time:
            if await self.user_input.fail.invalid_time_string_format(interaction, event_time): return
        event_datetime = self.user_input.correction.combine_date_time_change(event.time, event_date, event_time)
        if await self.user_input.fail.event_time_in_past(interaction, event_datetime): return
        if use_support is None: use_support = old_event.use_support
        is_type_change = event_type and event_type != old_event.type
        is_passcode_change = not auto_passcode is None and old_event.auto_passcode != auto_passcode
        is_time_change = old_event.time != event_datetime
        is_support_change = not use_support is None and old_event.use_support != use_support
        if is_type_change:
            await self.ui_recruitment_post.remove(interaction.guild_id, event_id)
        old_event = copy.deepcopy(old_event)
        event = Schedule(interaction.guild_id).edit(event_id, raid_leader, event_type, event_datetime,
                         self.user_input.correction.escape_event_description(description), auto_passcode, use_support)
        if is_type_change:
            await self.ui_recruitment_post.create(interaction.guild_id, event_id)
        if is_time_change or is_passcode_change or is_support_change:
            event.recreate_tasks()
        await self.ui_schedule.rebuild(interaction.guild_id)
        await self.ui_recruitment_post.rebuild(interaction.guild_id, event_id, True)
        changes = event.get_changes(interaction, old_event)
        await feedback_and_log(interaction, f'adjusted run #{str(event_id)}:\n{changes}')

    @add.autocomplete('event_type')
    @edit.autocomplete('event_type')
    async def autocomplete_schedule_type(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().event_type(interaction, current)

    @edit.autocomplete('raid_leader')
    async def autocomplete_leader(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().raid_leader(interaction, current)

    @add.autocomplete('event_date')
    @edit.autocomplete('event_date')
    async def autocomplete_schedule_date(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().date(current)

    @add.autocomplete('event_time')
    @edit.autocomplete('event_time')
    async def autocomplete_schedule_time(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().time(current)

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
