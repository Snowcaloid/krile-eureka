from datetime import datetime
import bot
import data.cache.message_cache as cache
from typing import Optional
from discord.ext.commands import GroupCog
from discord import Interaction, TextChannel
from discord.app_commands import check, command
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.tasks.tasks import TaskExecutionType
from data.ui.buttons import ButtonType, save_buttons
from data.runtime_processes import RunTimeProcessType
from data.validation.input_validator import InputValidator
from data.validation.process_validator import ProcessValidator
from logger import guild_log_message
from utils import default_defer, default_response, set_default_footer

from data.validation.permission_validator import PermissionValidator

###################################################################################
# embeds
###################################################################################
class EmbedCommands(GroupCog, group_name='embed', group_description='Commands for creating an embed.'):
    async def debug_followup(self, interaction: Interaction):
        await interaction.followup.send(
            embed=bot.instance.data.embed_controller.get(interaction.user.id).create_embed(True),
            view=bot.instance.data.embed_controller.get(interaction.user.id).create_view(True),
            ephemeral=True)

    #region creation
    @command(name = "create", description = "Initialize creation process of an embed.")
    @check(PermissionValidator.is_admin)
    async def create(self, interaction: Interaction, title: str, thumbnail: Optional[str] = None,
                     image: Optional[str] = None):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_another_process_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        bot.instance.data.processes.start(interaction.user.id, RunTimeProcessType.EMBED_CREATION)
        embed_data = bot.instance.data.embed_controller.get(interaction.user.id)
        embed_data.title = title
        embed_data.thumbnail = thumbnail
        embed_data.image = image
        await self.debug_followup(interaction)

    @command(name = "edit", description = "Edit embed title/thumbnail/image.")
    @check(PermissionValidator.is_admin)
    async def edit(self, interaction: Interaction, title: Optional[str] = None, thumbnail: Optional[str] = None,
                   image: Optional[str] = None):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        embed_data = bot.instance.data.embed_controller.get(interaction.user.id)
        if title:
            embed_data.title = title
        if thumbnail:
            embed_data.thumbnail = thumbnail
        if image:
            embed_data.image = image
        await self.debug_followup(interaction)

    @command(name = "load", description = "Load an embed for editing/creation process.")
    @check(PermissionValidator.is_admin)
    async def load(self, interaction: Interaction, channel: TextChannel, message_id: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_another_process_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_message_exists(interaction, channel, message_id): return
        if not await InputValidator.RAISING.check_message_contains_an_embed(interaction, channel, message_id): return
        message = await cache.messages.get(int(message_id), channel)
        bot.instance.data.embed_controller.load_from_message(interaction.user.id, message)
        bot.instance.data.processes.start(interaction.user.id, RunTimeProcessType.EMBED_CREATION)
        await self.debug_followup(interaction)

    @command(name = "post", description = "Post the embed.")
    @check(PermissionValidator.is_admin)
    async def finish(self, interaction: Interaction, channel: Optional[TextChannel] = None):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        embed_data = bot.instance.data.embed_controller.get(interaction.user.id)
        channel = interaction.channel if channel is None else channel
        message = await channel.send(embed=embed_data.create_embed(False))
        await message.edit(view=embed_data.create_view(False, message))
        save_buttons(message)
        await set_default_footer(message)
        await default_response(interaction, f'A message has been sent: {message.jump_url}.')
        bot.instance.data.processes.stop(interaction.user.id, RunTimeProcessType.EMBED_CREATION)

    @command(name = "replace", description = "Replace an embed.")
    @check(PermissionValidator.is_admin)
    async def replace(self, interaction: Interaction, channel: TextChannel, message_id: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_message_exists(interaction, channel, message_id): return
        if not await InputValidator.RAISING.check_message_author_is_self(interaction, channel, message_id): return
        embed_data = bot.instance.data.embed_controller.get(interaction.user.id)
        message = await cache.messages.get(message_id, channel)
        bot.instance.data.ui.view.delete(message_id)
        await message.edit(embed=embed_data.create_embed(False),
                           view=embed_data.create_view(False, message))
        save_buttons(message)
        await set_default_footer(message)
        await default_response(interaction, f'The message embed has been replaced: {message.jump_url}.')
        bot.instance.data.processes.stop(interaction.user.id, RunTimeProcessType.EMBED_CREATION)
    #endregion

    #region description
    @command(name = "description_add", description = "Add description to the embed.")
    @check(PermissionValidator.is_admin)
    async def description_add(self, interaction: Interaction, description: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        bot.instance.data.embed_controller.get(interaction.user.id).add_desc_line(description)
        await self.debug_followup(interaction)

    @command(name = "description_add_blank", description = "Add a new empty line to the description of the embed.")
    @check(PermissionValidator.is_admin)
    async def description_add_blank(self, interaction: Interaction):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        bot.instance.data.embed_controller.get(interaction.user.id).add_desc_line('')
        await self.debug_followup(interaction)

    @command(name = "description_edit", description = "Edit description line in the embed.")
    @check(PermissionValidator.is_admin)
    async def description_edit(self, interaction: Interaction, id: int, description: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        bot.instance.data.embed_controller.get(interaction.user.id).edit_desc_line(id, description)
        await self.debug_followup(interaction)

    @command(name = "description_remove", description = "Remove description from the embed.")
    @check(PermissionValidator.is_admin)
    async def description_remove(self, interaction: Interaction, id: int):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        bot.instance.data.embed_controller.get(interaction.user.id).remove_desc_line(id)
        await self.debug_followup(interaction)
    #endregion

    #region field
    @command(name = "field_add", description = "Add a field to the embed.")
    @check(PermissionValidator.is_admin)
    async def field_add(self, interaction: Interaction, title: str, description: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        bot.instance.data.embed_controller.get(interaction.user.id).add_field({"title": title, "desc": description, "id": 0})
        await self.debug_followup(interaction)

    @command(name = "field_edit", description = "Edit a field in the embed.")
    @check(PermissionValidator.is_admin)
    async def field_edit(self, interaction: Interaction, id: int, title: str, description: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_embed_contains_field(interaction, id): return
        bot.instance.data.embed_controller.get(interaction.user.id).edit_field({"title": title, "desc": description, "id": id})
        await self.debug_followup(interaction)

    @command(name = "field_remove", description = "Remove a field from the embed.")
    @check(PermissionValidator.is_admin)
    async def field_remove(self, interaction: Interaction, id: int):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_embed_contains_field(interaction, id): return
        bot.instance.data.embed_controller.get(interaction.user.id).remove_field(id)
        await self.debug_followup(interaction)
    #endregion

    #region button
    @command(name = "button_add", description = "Add role button to the embed.")
    @check(PermissionValidator.is_admin)
    async def button_add(self, interaction: Interaction, label: str, button_type: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_valid_button_type(interaction, button_type): return
        if button_type: button_type = ButtonType(button_type)
        bot.instance.data.embed_controller.get(interaction.user.id).add_button(label, button_type)
        await self.debug_followup(interaction)

    @command(name = "button_edit", description = "Edits a role button in the embed.")
    @check(PermissionValidator.is_admin)
    async def button_edit(self, interaction: Interaction, label: str, new_label: Optional[str] = None,
                          button_type: Optional[str] = None):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_embed_contains_button(interaction, label): return
        if not await InputValidator.RAISING.check_valid_button_type(interaction, button_type): return
        if button_type: button_type = ButtonType(button_type)
        bot.instance.data.embed_controller.get(interaction.user.id).edit_button(label, new_label, button_type)
        await self.debug_followup(interaction)

    @command(name = "button_remove", description = "Removes role button from the embed.")
    @check(PermissionValidator.is_admin)
    async def button_remove(self, interaction: Interaction, label: str):
        await default_defer(interaction)
        if not await ProcessValidator.RAISING.check_process_is_running(interaction, RunTimeProcessType.EMBED_CREATION): return
        if not await InputValidator.RAISING.check_embed_contains_button(interaction, label): return
        bot.instance.data.embed_controller.get(interaction.user.id).remove_button(label)
        await self.debug_followup(interaction)

    @button_add.autocomplete('button_type')
    @button_edit.autocomplete('button_type')
    async def autocomplete_button_type(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.button_type(current)
    #endregion

    #region error-handling
    @create.error
    @load.error
    @finish.error
    @description_add.error
    @description_add_blank.error
    @description_edit.error
    @description_remove.error
    @field_add.error
    @field_edit.error
    @field_remove.error
    @button_add.error
    @button_edit.error
    @button_remove.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command.', ephemeral=True)
    #endregion
