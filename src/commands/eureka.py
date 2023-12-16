import bot
from discord.ext.commands import GroupCog
from discord.app_commands import command
from discord import Embed, Interaction
from utils import default_defer, default_response
from logger import guild_log_message


class EurekaCommands(GroupCog, group_name='eureka', group_description='Eureka commands.'):
    @command(name = "weather", description = "Get weather information.")
    async def weather(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await interaction.channel.send(embed=Embed(description='...'))
        message = await bot.instance.data.ui.weather_post.rebuild(interaction.guild_id, message)
        await default_response(interaction, f'{message.jump_url}')

    #region error-handling
    @weather.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion