from discord.ext.commands import GroupCog
from discord.app_commands import command
from discord import Interaction
from utils.functions import default_defer, default_response
from utils.logger import guild_log_message


class EurekaCommands(GroupCog, group_name='eureka', group_description='Eureka commands.'):
    from data.ui.ui_weather_post import UIWeatherPost
    @UIWeatherPost.bind
    def ui_weather_post(self) -> UIWeatherPost: ...

    @command(name = "weather", description = "Get weather information.")
    async def weather(self, interaction: Interaction, share_with_others: bool = False):
        await default_defer(interaction, not share_with_others)
        message = await default_response(interaction, '_ _')
        await self.ui_weather_post.rebuild(interaction.guild_id, message)

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