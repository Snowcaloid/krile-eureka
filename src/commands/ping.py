import bot
from discord import Interaction, Role
from discord.ext.commands import GroupCog
from discord.app_commands import check, command, Choice
from data.table.pings import PingType
from data.table.schedule import ScheduleType, schedule_type_desc
from logger import guild_log_message
from utils import default_defer, default_response
from validation import get_raid_leader_permissions, permission_admin

###################################################################################
# pings
##################################################################################
class PingCommands(GroupCog, group_name='ping', group_description='Commands regarding pinging on certain embeds.'):
    @command(name='add_role', description='Add a ping for an embed.')
    @check(permission_admin)
    async def add_role(self, interaction: Interaction, ping_type: int, schedule_type: str, role: Role):
        await default_defer(interaction)
        bot.krile.data.pings.add_ping(interaction.guild_id, PingType(ping_type), ScheduleType(schedule_type), role.id)
        feedback = f'added a ping for role **{role.name}** on event <{PingType(ping_type).name}, {schedule_type_desc(schedule_type)}>'
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** {feedback}')
        await default_response(interaction, 'You ' + feedback)

    @command(name='remove_role', description='Add a ping for an embed.')
    @check(permission_admin)
    async def remove_role(self, interaction: Interaction, ping_type: int, schedule_type: str, role: Role):
        await default_defer(interaction)
        bot.krile.data.pings.remove_ping(interaction.guild_id, PingType(ping_type), ScheduleType(schedule_type), role.id)
        feedback = f'removed a ping for role **{role.name}** on event <{PingType(ping_type).name}, {schedule_type_desc(schedule_type)}>'
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** {feedback}')
        await default_response(interaction, 'You ' + feedback)

    async def autocomplete_schedule_type(self, interaction: Interaction, current: str):
        allow_ba, allow_drs = get_raid_leader_permissions(interaction.user)
        ba_runs = [
            Choice(name='BA Normal Run',  value=ScheduleType.BA_NORMAL.value),
            Choice(name='BA Reclear Run', value=ScheduleType.BA_RECLEAR.value),
            Choice(name='BA Special Run', value=ScheduleType.BA_SPECIAL.value)
        ]
        drs_runs = [
            Choice(name='DRS Normal Run',  value=ScheduleType.DRS_NORMAL.value),
            Choice(name='DRS Reclear Run', value=ScheduleType.DRS_RECLEAR.value)
        ]
        result = [Choice(name='Custom run (define by yourself in description)', value=ScheduleType.CUSTOM.value)]
        if allow_ba:
            result += ba_runs
        if allow_drs:
            result += drs_runs
        return result

    @add_role.autocomplete('ping_type')
    @remove_role.autocomplete('ping_type')
    async def autocomplete_ping_type(self, interaction: Interaction, current: str):
        return [
            Choice(name='Main passcodes',  value=PingType.MAIN_PASSCODE.value),
            Choice(name='Support passcodes', value=PingType.SUPPORT_PASSCODE.value),
            Choice(name='Party leader posts', value=PingType.PL_POST.value)
        ]

    @add_role.autocomplete('schedule_type')
    @remove_role.autocomplete('schedule_type')
    async def autocomplete_schedule_type_with_all(self, interaction: Interaction, current: str):
        allow_ba, allow_drs = get_raid_leader_permissions(interaction.user)
        result = await self.autocomplete_schedule_type(interaction, current)
        if allow_ba:
            result.append(Choice(name='All BA Runs', value=ScheduleType.BA_ALL.value))
        if allow_drs:
            result.append(Choice(name='All DRS Runs', value=ScheduleType.DRS_ALL.value))
        return result

    #region error-handling
    @add_role.error
    @remove_role.error
    async def handle_permission_admin(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command  or an error has occured.', ephemeral=True)
    #endregion