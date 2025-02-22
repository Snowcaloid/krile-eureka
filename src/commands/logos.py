from discord.ext.commands import GroupCog
from discord.app_commands import command
from discord import Interaction
from utils import default_defer, default_response
from logger import guild_log_message


class LogosCommands(GroupCog, group_name='logos', group_description='Logos action commands.'):
    from data.ui.ui_help import UIHelp
    @UIHelp.bind
    def ui_help(self) -> UIHelp: ...

    @command(name = "crafting", description = "Guide to crafting logos actions")
    async def crafting(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_crafting(message)

    @command(name = "wisdoms", description = "Spirit of the remembered + Wisdom explanations")
    async def wisdoms(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_wisdoms(message)

    @command(name = "actions", description = "Logos action detailed explanations")
    async def actions(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_actions(message)

    @command(name = "tank", description = "Tank logos actions")
    async def tank(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_tank(message)

    @command(name = "healer", description = "Healer logos actions")
    async def healer(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_healer(message)

    @command(name = "melee", description = "Melee logos actions")
    async def melee(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_melee(message)

    @command(name = "ranged", description = "Ranged/Mage logos actions")
    async def ranged(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_ranged(message)

    @command(name = "mage", description = "Ranged/Mage logos actions")
    async def mage(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_ranged(message)

    @command(name = "utility", description = "Utility logos actions")
    async def utility(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_utility(message)

    @command(name = "website", description = "https://ffxiv-eureka.com/logograms")
    async def website(self, interaction: Interaction):
        await default_defer(interaction, False)
        message = await default_response(interaction, '_ _')
        await self.ui_help.logos_website(message)

    #region error-handling
    @crafting.error
    @wisdoms.error
    @actions.error
    @tank.error
    @healer.error
    @melee.error
    @ranged.error
    @mage.error
    @utility.error
    @website.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion