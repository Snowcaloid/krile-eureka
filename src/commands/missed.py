from datetime import datetime, timedelta
from discord.ext.commands import GroupCog
import bot
from discord import Embed, Interaction
from discord.app_commands import check, command
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.tasks.tasks import TaskExecutionType
from data.validation.input_validator import InputValidator
from logger import guild_log_message
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator

###################################################################################
# missed runs
###################################################################################
class MissedCommands(GroupCog, group_name='missed', group_description='Commands regarding missed runs.'):
    @command(name='run', description='Create a missed run post for 10 minutes.')
    @check(PermissionValidator.is_raid_leader)
    async def run(self, interaction: Interaction, event_category: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_category(interaction, event_category): return
        message = await interaction.channel.send(embed=Embed(description='...'))
        await bot.instance.data.ui.missed_run_post.rebuild(interaction.guild_id, message, event_category)
        bot.instance.data.tasks.add_task(
            datetime.utcnow() + timedelta(minutes=10),
            TaskExecutionType.REMOVE_MISSED_RUN_POST,
            {"guild": interaction.guild_id, "channel": interaction.channel.id, "message": message.id})
        await default_response(interaction, 'Posted.')

    @command(name='accept', description='Accept early passcode request.')
    @check(PermissionValidator.is_raid_leader)
    async def accept(self, interaction: Interaction, user: str, event_category: str):
        await default_defer(interaction, False)
        if not await bot.instance.get_guild(interaction.guild_id).fetch_member(int(user)):
            return await default_response(interaction, 'The requested user cannot be found on this server.')
        bot.instance.data.guilds.get(interaction.guild_id).missed_runs.remove(int(user), event_category)
        await bot.instance.data.ui.missed_runs_list.rebuild(interaction.guild_id)
        await default_response(interaction, 'User has been accepted and removed from the early passcode list.')

    @accept.autocomplete('user')
    async def autocomplete_user_name(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.guild_member(interaction, current)

    @run.autocomplete('event_category')
    @accept.autocomplete('event_category')
    async def autocomplete_event_categories_short(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_categories_short(current)

    #region error-handling
    @run.error
    @accept.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command.', ephemeral=True)
    #endregion