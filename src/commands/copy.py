import bot
import data.cache.message_cache as cache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction
from discord.channel import TextChannel
from data.runtime_processes import RunTimeProcessType
from data.validation.input_validator import InputValidator
from data.validation.process_validator import ProcessValidator
from utils import default_defer, default_response, set_default_footer
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message


class CopyCommands(GroupCog, group_name='copy', group_description='Copy commands.'):
    @command(name = "message", description = "Copy a message posted by anyone.")
    @check(PermissionValidator.is_admin)
    async def message(self, interaction: Interaction, channel: TextChannel, message_id: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_another_process_running(interaction, RunTimeProcessType.COPYING_MESSAGE): return
        bot.instance.data.processes.start(interaction.user.id, RunTimeProcessType.COPYING_MESSAGE)
        message = await cache.messages.get(str(message_id), channel)
        bot.instance.data.message_copy_controller.add(interaction.user.id, message)
        await default_response(interaction, f'Copied message.')

    @command(name = "post", description = "Post the copied message in a channel.")
    @check(PermissionValidator.is_admin)
    async def post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.COPYING_MESSAGE): return
        message = bot.instance.data.message_copy_controller.get(interaction.user.id)
        message = await channel.send(message.content, embeds=message.embeds)
        await set_default_footer(message)
        bot.instance.data.processes.stop(interaction.user.id, RunTimeProcessType.COPYING_MESSAGE)
        await default_response(interaction, f'Sent the message: {message.jump_url}.')

    @command(name = "replace", description = "Replace a message with the copied message.")
    @check(PermissionValidator.is_admin)
    async def replace(self, interaction: Interaction, channel: TextChannel, message_id: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.COPYING_MESSAGE): return
        if not await InputValidator.RAISING.check_message_exists(interaction, channel, str(message_id)): return
        message_source = bot.instance.data.message_copy_controller.get(interaction.user.id)
        message_dest = await cache.messages.get(str(message_id), channel)
        message_dest = await message_dest.edit(content=message_source.content, embeds=message_source.embeds)
        await set_default_footer(message_dest)
        bot.instance.data.processes.stop(interaction.user.id, RunTimeProcessType.COPYING_MESSAGE)
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