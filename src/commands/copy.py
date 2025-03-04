from data.cache.message_cache import MessageCache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction, Thread
from discord.channel import TextChannel
from data.validation.input_validator import InputValidator
from utils.functions import default_defer, default_response
from data.validation.permission_validator import PermissionValidator
from utils.logger import guild_log_message


class CopyCommands(GroupCog, group_name='copy', group_description='Copy commands.'):
    from data.ui.copied_messages import MessageCopyController
    @MessageCopyController.bind
    def message_copy_controller(self) -> MessageCopyController: ...

    @command(name = "message", description = "Copy a message posted by anyone.")
    @check(PermissionValidator().is_admin)
    async def message(self, interaction: Interaction, channel: TextChannel, message_id: str):
        await default_defer(interaction)
        message = await MessageCache().get(str(message_id), channel)
        self.message_copy_controller.add(interaction.user.id, message)
        await default_response(interaction, f'Copied message.\n{message.content}')

    @command(name = "post", description = "Post the copied message in a channel.")
    @check(PermissionValidator().is_admin)
    async def post(self, interaction: Interaction, channel: TextChannel | Thread):
        await default_defer(interaction)
        message = self.message_copy_controller.get(interaction.user.id)
        message = await channel.send(message.content, embeds=message.embeds, files=[await a.to_file() for a in message.attachments])
        await default_response(interaction, f'Sent the message: {message.jump_url}.')

    @command(name = "replace", description = "Replace a message with the copied message.")
    @check(PermissionValidator().is_admin)
    async def replace(self, interaction: Interaction, channel: TextChannel | Thread, message_id: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_message_exists(interaction, channel, str(message_id)): return
        message_source = self.message_copy_controller.get(interaction.user.id)
        message_dest = await MessageCache().get(str(message_id), channel)
        message_dest = await message_dest.edit(content=message_source.content, embeds=message_source.embeds,
                                               attachments=[await a.to_file() for a in message_source.attachments])
        await default_response(interaction, f'Edited the message: {message_dest.jump_url}.')

    #region error-handling
    @message.error
    @post.error
    @replace.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion