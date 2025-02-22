from discord.ext.commands import GroupCog
from discord.app_commands import command
from discord import Interaction
from utils import default_defer, default_response
from logger import guild_log_message


class BACommands(GroupCog, group_name='ba', group_description='Baldesion Arsenal commands.'):
    from data.ui.ui_help import UIHelp
    @UIHelp.bind
    def ui_help(self) -> UIHelp: ...

    @command(name = "portals", description = "BA Map with portals macro")
    async def portals(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_portals(message)

    @command(name = "rooms", description = "BA Rooms Image")
    async def rooms(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_rooms(message)

    @command(name = "raiden", description = "BA Raiden Waymarks")
    async def raiden(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_raiden(message)

    @command(name = "av", description = "BA AV Waymarks")
    async def av(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_av(message)

    @command(name = "ozma", description = "BA Ozma help post")
    async def ozma(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_ozma(message)

    @command(name = "fairy", description = "Hydatos Fairy guide")
    async def fairy(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_fairy(message)

    @command(name = "trapping", description = "BA trapping guide")
    async def trapping(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_trapping(message)

    @command(name = "entrance", description = "BA entrance guide")
    async def entrance(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.ba_entrance(message)

    #region error-handling
    @portals.error
    @rooms.error
    @ozma.error
    @av.error
    @raiden.error
    @fairy.error
    @trapping.error
    @entrance.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion