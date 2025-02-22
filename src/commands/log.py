from discord import Interaction
from discord.ext.commands import GroupCog
from discord.channel import TextChannel
from discord.app_commands import check, command
from basic_types import GuildChannelFunction
from logger import feedback_and_log, guild_log_message
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator

###################################################################################
# logging
##################################################################################
class LogCommands(GroupCog, group_name='log', group_description='Commands regarding logging events in the log channel.'):
    from data.guilds.guild import Guilds
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    @command(name='channel', description='Set the channel to use for logging events.')
    @check(PermissionValidator().is_admin)
    async def channel(self, interaction: Interaction, target_channel: TextChannel):
        await default_defer(interaction)
        self.guilds.get(interaction.guild_id).channels.set(target_channel.id, GuildChannelFunction.LOGGING)
        await feedback_and_log(interaction, f'set the log channel to {target_channel.jump_url}.')


    @command(name='disable', description='Stop sending messages to the logging channel.')
    @check(PermissionValidator().is_admin)
    async def disable(self, interaction: Interaction):
        await default_defer(interaction)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has disabled logging, good bye!')
        self.guilds.get(interaction.guild_id).channels.remove(GuildChannelFunction.LOGGING)
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