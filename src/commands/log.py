import bot
from discord import Interaction
from discord.ext.commands import GroupCog
from discord.channel import TextChannel
from discord.app_commands import check, command
from data.guilds.guild_channel_functions import GuildChannelFunction
from logger import guild_log_message
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator

###################################################################################
# logging
##################################################################################
class LogCommands(GroupCog, group_name='log', group_description='Commands regarding logging events in the log channel.'):
    @command(name='channel', description='Set the channel to use for logging events.')
    @check(PermissionValidator.is_admin)
    async def channel(self, interaction: Interaction, target_channel: TextChannel):
        await default_defer(interaction)
        # Handle the change in the database.
        bot.instance.data.guilds.get(interaction.guild_id).channels.set(target_channel.id, GuildChannelFunction.LOGGING)
        # Record this change to the log.
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** set the log channel.')
        # Privately respond to the user with the outcome.
        await default_response(interaction, f'The log channel has been set to {target_channel.mention}.')


    @command(name='disable', description='Stop sending messages to the logging channel.')
    @check(PermissionValidator.is_admin)
    async def disable(self, interaction: Interaction):
        await default_defer(interaction)
        # Send one final message so the log has a record that it was turned off.
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has disabled logging, good bye!')
        # Remove the log channel
        bot.instance.data.guilds.get(interaction.guild_id).channels.remove(GuildChannelFunction.LOGGING)
        # Privately let the user know we have turned logging off.
        await default_response(interaction, 'Messages will no longer be sent to the log channel.')

    #region error-handling
    @channel.error
    @disable.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command.', ephemeral=True)
    #endregion