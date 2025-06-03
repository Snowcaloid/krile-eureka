from data.cache.message_cache import MessageCache
from models.button.discord_button import DiscordButton
from models.button.button_template import ButtonTemplate
from utils.basic_types import ButtonType
from utils.logger import GuildLogger
from utils.functions import default_defer, default_response

from discord import Interaction, Member

class RoleSelectionButton(ButtonTemplate):
    """Buttons, which add or remove a role from the user who interacts with them"""
    @MessageCache.bind
    def _message_cache(self) -> MessageCache: return ...

    def button_type(self) -> ButtonType: return ButtonType.ROLE_SELECTION
    

    async def callback(self, interaction: Interaction, button: DiscordButton):
        await default_defer(interaction)
        if isinstance(interaction.user, Member):
            role = interaction.guild.get_role(button.button_struct.role_id) 
            if role is None:
                message = await self._message_cache.get(button.button_struct.message_id,
                                                        interaction.guild.get_channel(button.button_struct.channel_id))
                GuildLogger(interaction.guild_id).respond(interaction, f'tried using button <{button.label}> in message <{message}> but role is not loaded. Contact your administrators.')
            elif interaction.user.get_role(role.id):
                await interaction.user.remove_roles(role)
                GuildLogger(interaction.guild_id).respond(interaction, f'removed role **{role.name}** from {interaction.user.mention}.')
            else:
                await interaction.user.add_roles(role)
                GuildLogger(interaction.guild_id).respond(interaction, f'taken the role **{role.name}**.')
        else:
            await default_response(interaction, f'Role buttons don''t work outside of a server setting.')