
from discord.ext.commands import GroupCog
from discord import Interaction, TextChannel
from discord.app_commands import check, command
from utils.logger import guild_log_message

from data.validation.permission_validator import PermissionValidator

###################################################################################
# embeds
###################################################################################
class EmbedCommands(GroupCog, group_name='embed', group_description='Commands for creating an embed.'):
    from ui.ui_embed_builder import UI_Embed_Builder
    @UI_Embed_Builder.bind
    def ui_embed_builder(self) -> UI_Embed_Builder: ...

    from data.validation.user_input import UserInput
    @UserInput.bind
    def user_input(self) -> UserInput: ...

    from data.cache.message_cache import MessageCache
    @MessageCache.bind
    def message_cache(self) -> MessageCache: ...

    @command(name = "create", description = "Initialize creation process of an embed.")
    @check(PermissionValidator().is_admin)
    async def create(self, interaction: Interaction):
        await self.ui_embed_builder.create(interaction)

    @command(name = "load", description = "Load an embed for editing/creation process.")
    @check(PermissionValidator().is_admin)
    async def load(self, interaction: Interaction, channel: TextChannel, message_id: str):
        if await self.user_input.fail.message_not_found(interaction, channel, message_id): return
        if await self.user_input.fail.message_doesnt_contain_embeds(interaction, channel, message_id): return
        message = await self.message_cache.get(int(message_id), channel)
        await self.ui_embed_builder.load(interaction, message)

    #region error-handling
    @create.error
    @load.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command.', ephemeral=True)
    #endregion
