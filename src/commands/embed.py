from typing import Optional
from discord.ext.commands import GroupCog
import bot as cerp_bot
from discord import Embed, Interaction, Message, TextChannel
from discord.app_commands import check, command, Choice
from buttons import ButtonType
from data.embed_data import Error_MessageHasNoEmbeds
from data.query import QueryType
from utils import set_default_footer

from validation import permission_admin

###################################################################################
# embeds
###################################################################################
class EmbedCommands(GroupCog, group_name='embed', group_description='Commands for creating an embed.'):
    async def send_query_request_or_defer(self, interaction: Interaction):
        if not cerp_bot.snowcaloid.data.query.running(interaction.user.id, QueryType.EMBED):
            return await interaction.response.send_message(
                embed=Embed(title='Use /embed create to start the creation process.'),
                ephemeral=True)
        await interaction.response.defer(thinking=True, ephemeral=True)
        return None

    async def debug_followup(self, interaction: Interaction):
        await interaction.followup.send(
            embed=cerp_bot.snowcaloid.data.embeds.create_embed(interaction.user.id, True),
            view=cerp_bot.snowcaloid.data.embeds.create_view(interaction.user.id, True),
            ephemeral=True)
    
    #region create, edit & finish
    @command(name = "create", description = "Initialize creation process of an embed.")
    @check(permission_admin)
    async def create(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        cerp_bot.snowcaloid.data.query.start(interaction.user.id, QueryType.EMBED)
        await self.debug_followup(interaction)
        
    @command(name = "edit", description = "Initialize editing process of an embed.")
    @check(permission_admin)
    async def edit(self, interaction: Interaction, channel: TextChannel, message_id: str):
        if cerp_bot.snowcaloid.data.query.running(interaction.user.id, QueryType.EMBED):
            return await interaction.response.send_message(
                embed=Embed(title='Another embed process is currently running.'),
                ephemeral=True)
        await interaction.response.defer(thinking=True, ephemeral=True)
        message = await channel.fetch_message(int(message_id))
        if message:
            if cerp_bot.snowcaloid.user != message.author:
                return await interaction.followup.send('It\'s only possible to edit my own embeds.', ephemeral=True)
            try:
                cerp_bot.snowcaloid.data.embeds.load_from_embed(interaction.user.id, message)
                cerp_bot.snowcaloid.data.query.start(interaction.user.id, QueryType.EMBED)
            except Error_MessageHasNoEmbeds:
                return await interaction.followup.send('This message has no embeds.', ephemeral=True)
            await self.debug_followup(interaction)
        else:
            await interaction.followup.send('Invalid message id.', ephemeral=True)

    @command(name = "finish", description = "Finish and post the embed.")
    @check(permission_admin)
    async def finish(self, interaction: Interaction, channel: Optional[TextChannel] = None, button_type: Optional[str] = ''):
        if await self.send_query_request_or_defer(interaction):
            return
        type = ButtonType.ROLE_SELECTION
        if button_type:
            if button_type in ButtonType._value2member_map_:
                type = ButtonType(button_type)
            else:
                return await interaction.followup.send(f'Button type "{button_type}" is invalid.')
        embeds = cerp_bot.snowcaloid.data.embeds
        if channel is None:
            channel = interaction.channel
        message = embeds.get_entry(interaction.user.id).message
        if message is None:
            message: Message = await channel.send('.')
        message = await message.edit(
            embed=embeds.create_embed(interaction.user.id, False),
            view=embeds.create_view(interaction.user.id, False, message, type))
        await set_default_footer(message)
        if embeds.get_entry(interaction.user.id).message:
            await interaction.followup.send(f'The message has been edited.', ephemeral=True)
        else:
            await interaction.followup.send(f'A message has been sent to #{channel.name}.', ephemeral=True)
        cerp_bot.snowcaloid.data.query.stop(interaction.user.id, QueryType.EMBED)
    #endregion
      
    #region simple commands
    @command(name = "title", description = "Change title of the embed.")
    @check(permission_admin)
    async def title(self, interaction: Interaction, title: str):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.get_entry(interaction.user.id).title = title
        await self.debug_followup(interaction)
        
    @command(name = "image", description = "Change image of the embed.")
    @check(permission_admin)
    async def image(self, interaction: Interaction, url: str):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.get_entry(interaction.user.id).image = url
        await self.debug_followup(interaction)
        
    @command(name = "thumbnail", description = "Change thumbnail of the embed.")
    @check(permission_admin)
    async def thumbnail(self, interaction: Interaction, url: str):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.get_entry(interaction.user.id).thumbnail = url
        await self.debug_followup(interaction)
    #endregion
      
    #region description
    @command(name = "add_description", description = "Add description to the embed.")
    @check(permission_admin)
    async def add_description(self, interaction: Interaction, description: str):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.add_desc_line(interaction.user.id, description)
        await self.debug_followup(interaction)
        
    @command(name = "add_blank_description", description = "Add a new empty line to the description of the embed.")
    @check(permission_admin)
    async def add_blank_description(self, interaction: Interaction):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.add_desc_line(interaction.user.id, '')
        await self.debug_followup(interaction)
        
    @command(name = "edit_description", description = "Edit description line in the embed.")
    @check(permission_admin)
    async def edit_description(self, interaction: Interaction, id: int, description: str):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.edit_desc_line(interaction.user.id, id, description)
        await self.debug_followup(interaction)
        
    @command(name = "remove_description", description = "Remove description from the embed.")
    @check(permission_admin)
    async def remove_description(self, interaction: Interaction, id: int):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.remove_desc_line(interaction.user.id, id)
        await self.debug_followup(interaction)
    #endregion
      
    #region field
    @command(name = "add_field", description = "Add a field to the embed.")
    @check(permission_admin)
    async def add_field(self, interaction: Interaction, title: str, description: str):
        if await self.send_query_request_or_defer(interaction):
            return
        cerp_bot.snowcaloid.data.embeds.add_field(interaction.user.id, {"title": title, "desc": description, "id": 0})
        await self.debug_followup(interaction)
        
    @command(name = "edit_field", description = "Edit a field in the embed.")
    @check(permission_admin)
    async def edit_field(self, interaction: Interaction, id: int, title: str, description: str):
        if await self.send_query_request_or_defer(interaction):
            return
        if not cerp_bot.snowcaloid.data.embeds.field_exists(interaction.user.id, id):
            return await interaction.followup.send(f'#{id} doesn\'t exist yet.', ephemeral=True)
        cerp_bot.snowcaloid.data.embeds.edit_field(interaction.user.id, id, {"title": title, "desc": description, "id": id})
        await self.debug_followup(interaction)
        
    @command(name = "remove_field", description = "Remove a field from the embed.")
    @check(permission_admin)
    async def remove_field(self, interaction: Interaction, id: int):
        if await self.send_query_request_or_defer(interaction):
            return
        if not cerp_bot.snowcaloid.data.embeds.field_exists(interaction.user.id, id):
            return await interaction.followup.send(f'#{id} doesn\'t exist yet.', ephemeral=True)
        cerp_bot.snowcaloid.data.embeds.remove_field(interaction.user.id, id)
        await self.debug_followup(interaction)
    #endregion
    
    #region button
    @command(name = "add_button", description = "Add role button to the embed.")
    @check(permission_admin)
    async def add_button(self, interaction: Interaction, label: str):
        if await self.send_query_request_or_defer(interaction):
            return
        if cerp_bot.snowcaloid.data.embeds.button_exists(interaction.user.id, label):
            return await interaction.followup.send(f'Button {label} is already in the list. Try another name.', ephemeral=True)
        cerp_bot.snowcaloid.data.embeds.add_button(interaction.user.id, label)
        await self.debug_followup(interaction)
        
    @command(name = "edit_button", description = "Edits a role button in the embed.")
    @check(permission_admin)
    async def edit_button(self, interaction: Interaction, old_label: str, new_label: str):
        if await self.send_query_request_or_defer(interaction):
            return
        if not cerp_bot.snowcaloid.data.embeds.button_exists(interaction.user.id, old_label):
            return await interaction.followup.send(f'Button {old_label} doesn\'t exist yet.', ephemeral=True)
        cerp_bot.snowcaloid.data.embeds.edit_button(interaction.user.id, old_label, new_label)
        await self.debug_followup(interaction)
        
    @command(name = "remove_button", description = "Removes role button from the embed.")
    @check(permission_admin)
    async def remove_button(self, interaction: Interaction, label: str):
        if await self.send_query_request_or_defer(interaction):
            return
        if not cerp_bot.snowcaloid.data.embeds.button_exists(interaction.user.id, label):
            return await interaction.followup.send(f'Button {label} doesn\'t exist yet.', ephemeral=True)
        cerp_bot.snowcaloid.data.embeds.remove_button(interaction.user.id, label)
        await self.debug_followup(interaction)
    #endregion
    
    #region error-handling
    @create.error
    @edit.error
    @finish.error
    @title.error
    @image.error
    @thumbnail.error
    @add_description.error
    @add_blank_description.error
    @edit_description.error
    @remove_description.error
    @add_field.error
    @edit_field.error
    @remove_field.error
    @add_button.error
    @remove_button.error
    async def handle_permission_admin(self, interaction: Interaction, error):
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command.', ephemeral=True)
    #endregion
    
    @finish.autocomplete('button_type')
    async def autocomplete_button_type(self, interaction: Interaction, current: str):
        return filter(lambda c: c.name.lower().startswith(current.lower()), [
            Choice(name='Role selection Button', value=ButtonType.ROLE_SELECTION.value),
            Choice(name='Party leader Post Button (must end with party numeber or "s")', value=ButtonType.PL_POST.value),
            Choice(name='Missed run Button', value=ButtonType.MISSEDRUN.value),
        ])