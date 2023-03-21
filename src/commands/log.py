import bot
from discord import Interaction
from discord.ext.commands import GroupCog
from discord.channel import TextChannel
from discord.app_commands import check, command
from data.table.database import DatabaseOperation
from logger import guild_log_message
from validation import permission_admin

###################################################################################
# logging
##################################################################################
class LogCommands(GroupCog, group_name='log', group_description='Commands regarding logging events in the log channel.'):
    @command(name='channel', description='Set the channel to use for logging events.')
    @check(permission_admin)
    async def channel(self, interaction: Interaction, target_channel: TextChannel):
        # Handle the change in the database.
        result: DatabaseOperation = bot.krile.data.guild_data.set_log_channel(interaction.guild_id, target_channel.id)

        # Convert the result to something the user can understand.
        if result == DatabaseOperation.NONE:
            feedback = 'The log channel was already set to that.'
        elif result == DatabaseOperation.ADDED:
            feedback = 'The log channel has been set.'
        elif result == DatabaseOperation.EDITED:
            feedback = 'The log channel has been changed.'
        else:
            feedback = 'Unknown operation.'

        # Privately respond to the user with the outcome.
        await interaction.response.send_message(feedback, ephemeral=True)

        # Record this change to the log.
        await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** set the log channel: {feedback}')

    @command(name='disable', description='Stop sending messages to the logging channel.')
    @check(permission_admin)
    async def disable(self, interaction: Interaction):
        # Send one final message so the log has a record that it was turned off.
        await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has disabled logging, good bye!')

        # Remove the log channel
        bot.krile.data.guild_data.set_log_channel(interaction.guild_id, None)

        # Privately let the user know we have turned logging off.
        await interaction.response.send_message('Messages will no longer be sent to the log channel.')

    #region error-handling
    @channel.error
    @disable.error
    async def handle_permission_admin(self, interaction: Interaction, error):
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command.', ephemeral=True)
    #endregion