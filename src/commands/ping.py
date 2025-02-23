from centralized_data import Singleton
from discord.ext.commands import Bot
from discord import Interaction
from discord.ext.commands import GroupCog
from discord.app_commands import command
from data.generators.autocomplete_generator import AutoCompleteGenerator
from basic_types import GuildChannelFunction, NotoriousMonster
from basic_types import GuildPingType
from basic_types import NOTORIOUS_MONSTERS
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from data.validation.input_validator import InputValidator
from logger import guild_log_message
from utils import default_defer, default_response

###################################################################################
# pings
##################################################################################
class PingCommands(GroupCog, group_name='ping', group_description='Ping people for mob spawns.'):
    @command(name = "spawn", description = "Ping a Eureka NM.")
    async def spawn(self, interaction: Interaction, notorious_monster: str, text: str):
        await default_defer(interaction)
        notorious_monster = InputValidator.NORMAL.notorious_monster_name_to_type(notorious_monster)
        if not await InputValidator.RAISING.check_allowed_notorious_monster(interaction, notorious_monster): return
        channel_data = GuildChannels(interaction.guild_id).get(GuildChannelFunction.NM_PINGS, notorious_monster)
        if channel_data:
            channel = Singleton.get_instance(Bot).get_channel(channel_data.id)
            if channel:
                mentions = await GuildPings(interaction.guild_id).get_mention_string(GuildPingType.NM_PING, notorious_monster)
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
        return AutoCompleteGenerator().notorious_monster(current)

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
