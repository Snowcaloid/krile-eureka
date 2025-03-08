import copy
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction
from typing import Optional
from data.events.schedule import Schedule
from data.generators.autocomplete_generator import AutoCompleteGenerator
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

    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    @command(name = "add", description = "Add an entry to the schedule.")
    @check(PermissionValidator().is_raid_leader)
    async def add(self, interaction: Interaction, event_type: str,
                  event_date: str, event_time: str,
                  description: Optional[str] = '',
                  auto_passcode: Optional[bool] = True,
                  use_support: Optional[bool] = True):
        await default_defer(interaction, False)
        event_model = self.user_input.event_creation(
            interaction,
            {
                "raid_leader": interaction.user.id,
                "type": event_type,
                "date": event_date,
                "time": event_time,
                "description": description,
                "auto_passcode": auto_passcode,
                "use_support": use_support
            })
        if hasattr(interaction, 'signature'):
            sig = interaction.signature
            return await self.tasks.until_over(sig)
        Schedule(interaction.guild_id).add(event_model, interaction)

    @command(name = "cancel", description = "Cancel a schedule entry.")
    @check(PermissionValidator().is_raid_leader)
    async def cancel(self, interaction: Interaction, event_id: int):
        await default_defer(interaction, False)
        if not self.user_input.event_cancellation(interaction, event_id): return
        Schedule(interaction.guild_id).cancel(event_id, interaction)

    @command(name = "edit", description = "Edit an entry from the schedule.")
    @check(PermissionValidator().is_raid_leader)
    async def edit(self, interaction: Interaction, event_id: int, event_type: Optional[str] = None,
                   raid_leader: Optional[str] = None, event_date: Optional[str] = None,
                   event_time: Optional[str] = None, description: Optional[str] = None,
                   auto_passcode: Optional[bool] = None, use_support: Optional[bool] = None):
        await default_defer(interaction, False)
        changes = self.user_input.event_change(interaction, {
            "id": event_id,
            "type": event_type,
            "raid_leader": raid_leader,
            "date": event_date,
            "time": event_time,
            "description": description,
            "auto_passcode": auto_passcode,
            "use_support": use_support
        })
        if hasattr(interaction, 'signature'):
            sig = interaction.signature
            return await self.tasks.until_over(sig)
        Schedule(interaction.guild_id).edit(event_id, changes, interaction)

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
