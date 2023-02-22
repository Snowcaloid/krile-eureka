from datetime import datetime, timedelta
from discord.ext.commands import GroupCog
import bot
from discord import Embed, Interaction, TextChannel
from discord.app_commands import check, command, Choice
from buttons import ButtonType, MissedRunButton
from data.table.tasks import TaskExecutionType
from utils import button_custom_id, default_defer, default_response
from validation import permission_admin, permission_raid_leader
from views import PersistentView

###################################################################################
# missed runs
###################################################################################
class MissedCommands(GroupCog, group_name='missed', group_description='Commands regarding missed runs.'):
    @command(name = "create_list", description = "Create a missed run list.")
    @check(permission_admin)
    async def create_list(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        message = await channel.send('.')
        bot.snowcaloid.data.guild_data.save_missed_runs_post(interaction.guild_id, channel.id, message.id)
        await bot.snowcaloid.data.missed_runs.update_post(interaction.guild_id)
        await default_response(interaction, f'Missed run post has been created in #{channel.name}.')

    @command(name='run', description='Create a missed run post for 10 minutes.')
    @check(permission_raid_leader)
    async def run(self, interaction: Interaction):
        await default_defer(interaction)
        disclaimer = ''
        role_name = bot.snowcaloid.data.guild_data.get_data(interaction.guild_id).missed_role
        if role_name:
            disclaimer = f'\nPlease note that this function is exclusive to members with role "{role_name}".'
        message = await interaction.channel.send(
            embed=Embed(
                title='Have you just missed this run?',
                description=f'You can use the button in case you missed entrance to this run. This will save you to the list.{disclaimer}'
            )
        )
        view = PersistentView()
        view.add_item(MissedRunButton(
            label='the button',
            custom_id=button_custom_id('missed', message, ButtonType.MISSEDRUN)))
        await message.edit(view=view)
        bot.snowcaloid.data.tasks.add_task(
            datetime.utcnow() + timedelta(minutes=10),
            TaskExecutionType.REMOVE_MISSED_RUN_POST,
            {"guild": interaction.guild_id, "channel": interaction.channel.id, "message": message.id})
        await default_response(interaction, 'Posted.')

    @command(name='accept', description='Accept early passcode request.')
    @check(permission_raid_leader)
    async def accept(self, interaction: Interaction, user: str):
        await default_defer(interaction)
        if not await bot.snowcaloid.get_guild(interaction.guild_id).fetch_member(int(user)):
            return await default_response(interaction, 'The requested user cannot be found on this server.')
        bot.snowcaloid.data.missed_runs.remove(interaction.guild_id, int(user))
        await bot.snowcaloid.data.missed_runs.update_post(interaction.guild_id)
        await default_response(interaction, 'User has been removed from the early passcode list.')

    @create_list.error
    @run.error
    @accept.error
    async def handle_permission_admin(interaction: Interaction, error):
        await interaction.response.send_message('You have insufficient rights to use this command.')

    @accept.autocomplete('user')
    async def autocomplete_user_name(self, interaction: Interaction, current: str):
        users = []
        i = 0
        currentlower = current.lower()
        for member in interaction.guild.members:
            if member.nick:
                if member.nick.lower().startswith(currentlower):
                    users.append(Choice(name=member.nick, value=str(member.id)))
                    i += 1
            elif member.name.lower().startswith(currentlower):
                users.append(Choice(name=member.name, value=str(member.id)))
                i += 1
            if i == 25:
                break
        return users
