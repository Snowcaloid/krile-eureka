import bot
from discord import Interaction
from discord.ext.commands import GroupCog
from data.generators.autocomplete_generator import AutoCompleteGenerator
from logger import guild_log_message

###################################################################################
# pings
##################################################################################
class PingCommands(GroupCog, group_name='ping', group_description='Ping people for mob spawns.'):

    #region error-handling
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command  or an error has occured.', ephemeral=True)
    #endregion
