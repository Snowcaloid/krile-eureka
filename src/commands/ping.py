import bot
from discord import Interaction
from discord.ext.commands import GroupCog
from discord.app_commands import command
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.guilds.guild import Guilds
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.notorious_monsters import NOTORIOUS_MONSTERS, NotoriousMonster
from data.validation.input_validator import InputValidator
from logger import guild_log_message
from utils import default_defer, default_response

###################################################################################
# pings
##################################################################################
class PingCommands(GroupCog, group_name='ping', group_description='Ping people for mob spawns.'):
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    @command(name = "spawn", description = "Ping a Eureka NM.")
    async def spawn(self, interaction: Interaction, notorious_monster: str, text: str):
        await default_defer(interaction)
        notorious_monster = InputValidator.NORMAL.notorious_monster_name_to_type(notorious_monster)
        if not await InputValidator.RAISING.check_allowed_notorious_monster(interaction, notorious_monster): return
        guild_data = self.guilds.get(interaction.guild_id)
        channel_data = guild_data.channels.get(GuildChannelFunction.NM_PINGS, notorious_monster)
        if channel_data:
            channel = bot.instance.get_channel(channel_data.id)
            if channel:
                mentions = await guild_data.pings.get_mention_string(GuildPingType.NM_PING, notorious_monster)
                message = await channel.send(f'{mentions} Notification for {NOTORIOUS_MONSTERS[NotoriousMonster(notorious_monster)]} by {interaction.user.mention}: {text}')
                await default_response(interaction, f'Pinged: {message.jump_url}')
                await message.add_reaction('💀')
                await message.add_reaction('🔒')
            else:
                await default_response(interaction, 'This feature is currently not set up. Please contact your administrators')
        else:
            await default_response(interaction, 'This feature is currently not set up. Please contact your administrators')

    @spawn.autocomplete('notorious_monster')
    async def autocomplete_notorious_monster(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.notorious_monster(current)

    #region error-handling
    @spawn.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command  or an error has occured.', ephemeral=True)
    #endregion
