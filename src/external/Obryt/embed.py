#
# This file is part of Orbyt. (https://github.com/nxmrqlly/orbyt)
# Copyright (c) 2023-present Ritam Das
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import annotations
from abc import abstractmethod
from io import BytesIO
from typing import override
from uuid import uuid4
import aiohttp
import re
import json
import copy

import discord
from discord.ui import TextInput
from discord import ChannelType, TextChannel

from bot import Bot
from models.button.button_matrix import ButtonMatrix
from models.button.discord_button import DiscordButton
from utils.basic_types import BUTTON_TYPE_CHOICES, ButtonType
from ui.base_button import delete_buttons, save_buttons
from utils.basic_types import BUTTON_STYLE_CHOICES
from ui.views import TemporaryView
from utils.logger import guild_log_message
from utils.functions import find_nearest_role
from .utils.views import BaseView, message_jump_button
from .utils.constants import EMOJIS, HTTP_URL_REGEX
from .utils.text_format import truncate


class EmbedModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, parent_view: EmbedBuilderView) -> None:
        self.embed = _embed

        self.parent_view = parent_view

        self.em_title.default = _embed.title
        self.description.default = _embed.description

        _image = _embed.image
        if _image is not None:
            self.image.default = _image.url

        _thumbnail = _embed.thumbnail
        if _thumbnail is not None:
            self.thumbnail.default = _thumbnail.url

        check_color = _embed.color
        if check_color is not None:
            clr = _embed.color.to_rgb()

            self.color.default = f"rgb({clr[0]}, {clr[1]}, {clr[2]})"

        super().__init__(title="Edit Embed Components", timeout=None)

    em_title = TextInput(
        label="Title",
        placeholder="The title of the embed",
        style=discord.TextStyle.short,
        required=False,
        max_length=256)
    description = TextInput(
        label="Description",
        placeholder="Upto 4000 characters. Out of shared max characters (6000)\nLorem ipsum dolor sit amet.\n",
        style=discord.TextStyle.long,
        required=False,
        max_length=4000)
    image = TextInput(
        label="Image URL",
        placeholder="http://example.com/space.png",
        required=False,
        style=discord.TextStyle.short)
    thumbnail = TextInput(
        label="Thumbnail URL",
        placeholder="http://example.com/stars.png",
        required=False,
        style=discord.TextStyle.short)
    color = TextInput(
        label="Color",
        placeholder="Hex #FFFFFF | rgb(r, g, b)",
        required=False)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_copy = copy.deepcopy(self.embed)

        self.embed.title = self.em_title.value  # or self.embed.title
        self.embed.description = self.description.value  # or self.embed.description

        self.embed.set_image(url=self.image.value)
        self.embed.set_thumbnail(url=self.thumbnail.value)

        if self.color.value:
            self.embed.color = discord.Color.from_str(self.color.value)

        if len(self.embed) > 6000:
            self.parent_view.embed = embed_copy
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed too long; Exceeded 6000 characters.",
                ephemeral=True)
            return

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. Please check for the following:\nEmpty Embed / Invalid Color / Invalid URL(s)",
                ephemeral=True)
        else:
            raise error


class AuthorModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, parent_view: EmbedBuilderView) -> None:
        self.embed = _embed
        self.parent_view = parent_view

        self.author_name.default = _embed.author.name
        self.url.default = _embed.author.url
        self.icon_url.default = _embed.author.icon_url

        super().__init__(title="Edit Author Component", timeout=None)

    author_name = TextInput(
        label="Author Name",
        placeholder="The name of the author",
        style=discord.TextStyle.short,
        max_length=256,
        required=False)
    url = TextInput(
        label="Author URL",
        placeholder="http://example.com",
        required=False,
        style=discord.TextStyle.short)
    icon_url = TextInput(
        label="Author Icon URL",
        placeholder="http://example.com/astronaut.png",
        required=False,
        style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_copy = copy.deepcopy(self.embed)

        self.embed.set_author(name=self.author_name.value,
            url=self.url.value,
            icon_url=self.icon_url.value)
        if len(self.embed) > 6000:
            self.parent_view.embed = embed_copy
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed too long; Exceeded 6000 characters.",
                ephemeral=True)
            return

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. Please check your input: Invalid URL(s)",
                ephemeral=True)
        else:
            raise error


class FooterModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, parent_view: EmbedBuilderView) -> None:
        self.embed = _embed
        self.parent_view = parent_view

        self.text.default = _embed.footer.text
        self.icon_url.default = _embed.footer.icon_url

        super().__init__(title="Edit Footer Component", timeout=None)

    text = TextInput(
        label="Footer Text",
        placeholder="The text of the footer",
        style=discord.TextStyle.short,
        max_length=2048,
        required=False)
    icon_url = TextInput(
        label="Footer Icon URL",
        placeholder="http://example.com/astronaut.png",
        required=False,
        style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_copy = copy.deepcopy(self.embed)

        self.embed.set_footer(text=self.text.value,
            icon_url=self.icon_url.value)
        if len(self.embed) > 6000:
            self.parent_view.embed = embed_copy
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed too long; Exceeded 6000 characters.",
                ephemeral=True)
            return
        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. Please check your input: Invalid URL(s)",
                ephemeral=True)
        else:
            raise error


class URLModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, parent_view: EmbedBuilderView) -> None:
        self.embed = _embed

        self.parent_view = parent_view

        self.url.default = _embed.url

        super().__init__(title="Edit URL Component", timeout=None)

    url = TextInput(
        label="Title URL",
        placeholder="http://example.com")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_copy = copy.deepcopy(self.embed)

        if not self.embed.title:
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed must have a title.", ephemeral=True)
            return

        self.embed.url = self.url.value

        if len(self.embed) > 6000:
            self.parent_view.embed = embed_copy
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed too long; Exceeded 6000 characters.",
                ephemeral=True)
            return

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. Invalid URL",
                ephemeral=True)
        else:
            raise error


class AddFieldModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, parent_view: EmbedBuilderView) -> None:
        self.embed = _embed
        self.parent_view = parent_view

        super().__init__(title="Add Field", timeout=None)

    fl_name = TextInput(
        label="Field Name",
        placeholder="The name of the field",
        style=discord.TextStyle.short,
        max_length=256,
        required=True)
    value = TextInput(
        label="Field Value",
        placeholder="The value of the field",
        style=discord.TextStyle.long,
        max_length=1024,
        required=True)
    inline = TextInput(
        label="Inline?",
        placeholder="True/False | T/F || Yes/No | Y/N (default: True)",
        style=discord.TextStyle.short,
        max_length=5,
        required=False)
    index = TextInput(
        label="Index (Where to add the field)",
        placeholder="1 - 25 (default: 25)",
        style=discord.TextStyle.short,
        max_length=2,
        required=False)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_copy = copy.deepcopy(self.embed)

        inline_set = {
            "true": True,
            "t": True,
            "yes": True,
            "y": True,
            "false": False,
            "f": False,
            "no": False,
            "n": False,
        }
        if self.inline.value:
            inline = inline_set.get(self.inline.value.lower())
        else:
            inline = True

        index = (int(self.index.value) - 1 if self.index.value else len(self.embed.fields))

        self.embed.insert_field_at(index,
            name=self.fl_name.value,
            value=self.value.value,
            inline=inline)

        if len(self.embed) > 6000:
            self.parent_view.embed = embed_copy

            await interaction.response.send_message(f"{EMOJIS['no']} - Embed too long; Exceeded 6000 characters.",
                ephemeral=True)
            return

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. {str(error)}",
                ephemeral=True)
        else:
            guild_log_message(interaction.guild_id,f"{error} {type(error)} {isinstance(error, discord.HTTPException)}")
            raise error


class DeleteFieldDropdown(discord.ui.Select):
    def __init__(self,
        *,
        _embed: discord.Embed,
        parent_view: EmbedBuilderView):
        self.embed = _embed

        self.parent_view = parent_view

        options = [
            discord.SelectOption(label=truncate(f"{i+1}. {field.name}"),
                value=str(i))
            for i, field in enumerate(self.embed.fields)
        ]

        super().__init__(placeholder="Select a field", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.embed.remove_field(int(self.values[0]))
        if len(self.embed) == 0:
            self.embed.description = "Lorem ipsum dolor sit amet."

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.edit_message(content=f"{EMOJIS['yes']} - Field deleted.", view=None)


class EditFieldModal(discord.ui.Modal):
    fl_name = TextInput(
        label="Field Name",
        placeholder="The name of the field",
        style=discord.TextStyle.short,
        max_length=256,
        required=False)
    value = TextInput(
        label="Field Value",
        placeholder="The value of the field",
        style=discord.TextStyle.long,
        max_length=1024,
        required=False)
    inline = TextInput(
        label="Inline?",
        placeholder="True/False | T/F || Yes/No | Y/N",
        style=discord.TextStyle.short,
        max_length=5,
        required=False)
    index = TextInput(
        label="Index (Where to add the field)",
        placeholder="1 - 25 (default: 25)",
        style=discord.TextStyle.short,
        max_length=2,
        required=False)

    def __init__(self,
        *,
        _embed: discord.Embed,
        parent_view: EmbedBuilderView,
        field_index: int) -> None:
        self.embed = _embed

        self.parent_view = parent_view
        self._old_index = int(field_index)

        field = self.embed.fields[field_index]

        self.fl_name.default = field.name
        self.value.default = field.value
        self.inline.default = str(field.inline)
        self.index.default = str(field_index + 1)

        super().__init__(title=f"Editing Field {field_index+1}", timeout=None)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        embed_copy = copy.deepcopy(self.embed)

        inline_set = {
            "true": True,
            "t": True,
            "yes": True,
            "y": True,
            "false": False,
            "f": False,
            "no": False,
            "n": False,
        }
        inline = inline_set.get(self.inline.value.lower())

        if self.index.value:
            index = int(self.index.value) - 1
        else:
            index = len(self.embed.fields) - 1

        if index < 0 or index > len(self.embed.fields):
            raise IndexError("Index out of range.")

        if inline is None:
            raise ValueError("Inline value must be Boolean!")

        self.embed.remove_field(self._old_index)
        self.embed.insert_field_at(index, name=self.fl_name.value, value=self.value.value, inline=inline)

        if len(self.embed) > 6000:
            self.parent_view.embed = embed_copy

            await interaction.response.send_message(f"{EMOJIS['no']} - Embed too long; Exceeded 6000 characters.",
                ephemeral=True)
            return

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(embed=self.embed)
        await interaction.response.edit_message(content=f"{EMOJIS['yes']} - Field edited.", view=None)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.edit_message(
                content=f"{EMOJIS['no']} - Invalid Input: {str(error)}",
                view=None)
        elif isinstance(error, IndexError):
            await interaction.response.edit_message(
                content=f"{EMOJIS['no']} - Invalid Index: {str(error)}",
                view=None)
        else:
            raise error


class EditFieldDropdown(discord.ui.Select):
    def __init__(self,
        *,
        _embed: discord.Embed,
        parent_view: EmbedBuilderView):
        self.embed = _embed
        self.parent_view = parent_view

        options = [
            discord.SelectOption(label=truncate(f"{i+1}. {field.name}", 100),
                value=str(i))
            for i, field in enumerate(_embed.fields)
        ]

        super().__init__(placeholder="Select a field", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditFieldModal(_embed=self.embed,
                field_index=int(self.values[0]),
                parent_view=self.parent_view))
        await interaction.edit_original_response(view=None, content="Editing Field...")


class SendToChannelSelect(discord.ui.ChannelSelect):
    @Bot.bind
    def bot(self) -> Bot: ...

    def __init__(self, *, _embed: discord.Embed, buttons: ButtonMatrix):
        self.embed = _embed
        self.buttons = buttons

        super().__init__(placeholder="Select a channel.",
            channel_types=[
                ChannelType.text,
                ChannelType.news,
                ChannelType.private_thread,
                ChannelType.public_thread,
                ChannelType.voice,
            ])

    async def callback(self, interaction: discord.Interaction):
        # check if user has access to send messages to channel
        channel_id = self.values[0].id

        channel = self.bot._client.get_channel(channel_id)

        user_perms = channel.permissions_for(interaction.user)

        view = self.buttons.as_view(True)
        try:
            if user_perms.send_messages and user_perms.embed_links:
                msg = await channel.send(embed=self.embed, view=view)
                save_buttons(msg, view)

                confirmed_view = BaseView(timeout=180, target=interaction).add_item(message_jump_button(msg.jump_url))
                await interaction.response.edit_message(content=f"{EMOJIS['yes']} - Embed sent to {channel.mention}.",
                    view=confirmed_view)
            else:
                await interaction.response.edit_message(content=f"{EMOJIS['no']} - You have permission to send embeds in {channel.mention}.",
                    view=None)
        except discord.HTTPException:
            await interaction.response.edit_message(f"{EMOJIS['no']} - Couldn't send the embed in {channel.mention}.",
                view=None)


class ReplaceMessageModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, buttons: ButtonMatrix, channel: TextChannel, parent_view: EmbedBuilderView) -> None:
        self.embed = _embed
        self.buttons = buttons
        self.parent_view = parent_view
        self.channel = channel

        super().__init__(title="Edit Footer Component", timeout=None)

    message_id = TextInput(
        label="Message ID",
        placeholder="0000000000000000000",
        style=discord.TextStyle.short,
        max_length=25,
        required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        message = await self.channel.fetch_message(int(self.message_id.value))
        if message is None:
            raise ValueError('Invalid message ID')

        try:
            delete_buttons(message.id)
            view=self.buttons.as_view(True)
            msg = await message.edit(embed=self.embed, view=view)
            save_buttons(msg, view)

            confirmed_view = BaseView(timeout=180, target=interaction).add_item(message_jump_button(msg.jump_url))
            await interaction.response.edit_message(content=f"{EMOJIS['yes']} - Embed replaced in {self.channel.mention}.",
                view=confirmed_view)
        except discord.HTTPException:
            await interaction.response.edit_message(f"{EMOJIS['no']} - Couldn't replaced the embed in {self.channel.mention}.",
                view=None)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. Please check your input: Invalid URL(s)",
                ephemeral=True)
        else:
            raise error


class ReplaceChannelSelect(discord.ui.ChannelSelect):
    @Bot.bind
    def bot(self) -> Bot: ...

    def __init__(self, *, _embed: discord.Embed, buttons: ButtonMatrix, parent_view: BaseView):
        self.embed = _embed
        self.buttons = buttons
        self.parent_view = parent_view

        super().__init__(placeholder="Select a channel.",
            channel_types=[
                ChannelType.text,
                ChannelType.news,
                ChannelType.private_thread,
                ChannelType.public_thread,
                ChannelType.voice,
            ])

    async def callback(self, interaction: discord.Interaction):
        # check if user has access to send messages to channel
        channel_id = self.values[0].id
        channel = self.bot._client.get_channel(channel_id)
        await interaction.response.send_modal(ReplaceMessageModal(_embed=self.embed, buttons=self.buttons, channel=channel, parent_view=self.parent_view))


class AddButtonModal(discord.ui.Modal):
    def __init__(self, *, buttons: ButtonMatrix, parent_view: EmbedBuilderView, button: DiscordButton) -> None:
        self.buttons = buttons
        self.button = button
        self.parent_view = parent_view
        super().__init__(title="Add Button", timeout=None)

    button_label = TextInput(
        label="Button Label",
        placeholder="The text of the button",
        style=discord.TextStyle.short,
        max_length=50,
        required=True)
    button_type = TextInput(
        label="Button Type",
        placeholder="role/roledisp/r/rd",
        style=discord.TextStyle.short,
        max_length=10,
        required=True)
    role = TextInput(
        label="Role",
        placeholder="Partial or full role name",
        style=discord.TextStyle.short,
        max_length=50,
        required=False)
    emoji = TextInput(
        label="Emoji",
        placeholder="Windows Key + .",
        style=discord.TextStyle.short,
        max_length=2,
        required=False)
    color = TextInput(
        label="Color/Style",
        placeholder="grey/blue/red/green",
        style=discord.TextStyle.short,
        max_length=5,
        required=False)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        label = self.button_label.value
        emoji = self.emoji.value if len(self.emoji.value) > 0 else None
        role = None

        if self.color.value:
            if not self.color.value.lower() in BUTTON_STYLE_CHOICES:
                raise ValueError(f'{self.color.value.lower()} is not a valid color/style choice.')
            color = BUTTON_STYLE_CHOICES[self.color.value.lower()]
        else:
            color = discord.ButtonStyle.secondary

        if not self.button_type.value.lower() in BUTTON_TYPE_CHOICES:
            raise ValueError(f'{self.button_type.value.lower()} is not a valid button type.')

        button_type = BUTTON_TYPE_CHOICES[self.button_type.value.lower()]
        if button_type == ButtonType.ROLE_SELECTION:
            role = find_nearest_role(interaction.guild, self.role.value)
            if role is None:
                raise ValueError(f'{self.role.value} is not a valid role name.')

        self.button.emoji = emoji
        self.button.role = role
        self.button.label = label
        self.button.style = color
        self.button.custom_id = str(uuid4())
        self.button.template = self.button.button_templates.get(button_type)
        self.button.disabled = True
        self.buttons[self.button.row][self.button.index] = self.button

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(view=self.buttons.as_view())
        await interaction.response.edit_message(content=f"{EMOJIS['yes']} - Button added successfully.", view=None)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.send_message(f"{EMOJIS['no']} - Value Error. {str(error)}",
                ephemeral=True)
        else:
            await guild_log_message(interaction.guild_id,f"{error} {type(error)} {isinstance(error, discord.HTTPException)}")
            raise error

class EditButtonModal(discord.ui.Modal):
    button_label = TextInput(
        label="Button Label",
        placeholder="The text of the button",
        style=discord.TextStyle.short,
        max_length=50,
        required=True)
    button_type = TextInput(
        label="Button Type",
        placeholder="role/roledisp/r/rd",
        style=discord.TextStyle.short,
        max_length=10,
        required=True)
    role = TextInput(
        label="Role",
        placeholder="Partial or full role name",
        style=discord.TextStyle.short,
        max_length=50,
        required=False)
    emoji = TextInput(
        label="Emoji",
        placeholder="Windows Key + .",
        style=discord.TextStyle.short,
        max_length=2,
        required=False)
    color = TextInput(
        label="Color/Style",
        placeholder="grey/blue/red/green",
        style=discord.TextStyle.short,
        max_length=5,
        required=False)

    def __init__(self,
        *,
        buttons: ButtonMatrix,
        parent_view: EmbedBuilderView,
        button: DiscordButton) -> None:
        self.buttons = buttons

        self.parent_view = parent_view
        self.button = button

        self.button_label.default = button.label
        self.button_type.default = next(key for key, value in BUTTON_TYPE_CHOICES.items() if value == button.template.button_type())
        self.role.default = button.role.name if button.role.name is not None else ''
        self.color.default = next(key for key, value in BUTTON_STYLE_CHOICES.items() if value == button.style)
        self.emoji.default = str(button.emoji) if button.emoji is not None else ''

        super().__init__(title=f"Editing Button <{button.label}>", timeout=None)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        label = self.button_label.value
        emoji = self.emoji.value if len(self.emoji.value) > 0 else None
        role = None

        if self.color.value:
            if not self.color.value.lower() in BUTTON_STYLE_CHOICES:
                raise ValueError(f'{self.color.value.lower()} is not a valid color/style choice.')
            color = BUTTON_STYLE_CHOICES[self.color.value.lower()]
        else:
            color = discord.ButtonStyle.secondary

        if not self.button_type.value.lower() in BUTTON_TYPE_CHOICES:
            raise ValueError(f'{self.button_type.value.lower()} is not a valid button type.')

        button_type = BUTTON_TYPE_CHOICES[self.button_type.value.lower()]
        if button_type == ButtonType.ROLE_SELECTION:
            role = find_nearest_role(interaction.guild, self.role.value)
            if role is None:
                raise ValueError(f'{self.role.value} is not a valid role name.')
        self.button.label = label
        self.button.emoji = emoji
        self.button.role = role
        self.button.style = color
        self.button.template = self.button.button_templates.get(button_type)
        self.button.disabled = True
        self.parent_view.message = await self.parent_view.message.edit(view=self.buttons.as_view())
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.response.edit_message(content=f"{EMOJIS['no']} - Invalid Input: {str(error)}",
                view=None)
        elif isinstance(error, IndexError):
            await interaction.response.edit_message(content=f"{EMOJIS['no']} - Invalid Index: {str(error)}",
                view=None)
        else:
            raise error

class ChooseButtonDropdown(discord.ui.Select):
    @abstractmethod
    def function(self) -> str: ...
    @abstractmethod
    async def confirmed(self, interaction: discord.Interaction) -> None: ...

    def __init__(self,
        *,
        buttons: ButtonMatrix,
        parent_view: EmbedBuilderView):
        self.buttons = buttons
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label=truncate(f"R {str(button.row + 1)} C {str(button.index + 1)} - {button.label}"), value=self.buttons.index(button))
            for button in self.buttons if not button is None
        ]
        super().__init__(placeholder=f"Select a button to {self.function()}", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.confirmed(interaction)

class DeleteButtonDropdown(ChooseButtonDropdown):
    @override
    def function(self) -> str: return "remove"
    @override
    async def confirmed(self, interaction: discord.Interaction) -> None:
        index = int(self.values[0])
        if index >= 0:
            button = [button for button in self.buttons][index]
            self.buttons[button.row][button.index] = None
            del button
        else:
            return await interaction.response.edit_message(content=f"{EMOJIS['no']} - Invalid Index.")

        self.parent_view.update_counters()
        self.parent_view.message = await self.parent_view.message.edit(view=self.buttons.as_view())
        await interaction.response.edit_message(content=f"{EMOJIS['yes']} - Button deleted.", view=None)

class EditButtonDropdown(ChooseButtonDropdown):
    @override
    def function(self) -> str: return "edit"
    @override
    async def confirmed(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(EditButtonModal(buttons=self.buttons,
            button=[button for button in self.buttons][int(self.values[0])],
            parent_view=self.parent_view))

class MoveButtonDropdown(ChooseButtonDropdown):
    @override
    def function(self) -> str: return "move"
    @override
    async def confirmed(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(view=ButtonMatrixView(self.buttons, self.parent_view,
                                                              [button for button in self.buttons][int(self.values[0])]),
                                        content="Select where to move the button to.")

class ImportJSONModal(discord.ui.Modal):
    def __init__(self, *, _embed: discord.Embed, parent_view: EmbedBuilderView):
        self.embed = _embed
        self.parent_view = parent_view

        super().__init__(title="Import JSON")

    json_or_mystbin = discord.ui.TextInput(
        label="JSON or Mystbin URL",
        placeholder="Paste JSON or mystb.in link here.\n"
        "If your JSON is too long, use https://mystb.in/ to upload it.\n",
        required=True,
        style=discord.TextStyle.paragraph)

    async def get_mystb_file(self, paste_id: str) -> str:
        headers = {
            "content": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            sesh = await session.get(f"https://api.mystb.in/paste/{paste_id}", headers=headers)
            status_table = {
                401: "Unauthorised",
                404: "Not Found",
                422: "Unprocessable Entity",
            }
            if sesh.status != 200:
                raise ValueError(f"Unable to fetch from mystb.in, API Returned {sesh.status}: {status_table[sesh.status]}")

        json_str = json.loads(await sesh.content.read())["files"][0]["content"]
        return json_str

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not re.fullmatch(HTTP_URL_REGEX, self.json_or_mystbin.value):
            json_value = self.json_or_mystbin.value

        else:
            if not self.json_or_mystbin.value.startswith("https://mystb.in/"):
                return await interaction.followup.send(content=f"{EMOJIS['no']} - Not a mystb.in URL", ephemeral=True)

            json_value = await self.get_mystb_file(self.json_or_mystbin.value.lstrip("https://mystb.in/"))

        to_dict = json.loads(json_value,
            parse_int=lambda x: int(x),
            parse_float=lambda x: float(x))
        embed = discord.Embed.from_dict(to_dict)

        if len(embed) <= 0 or len(embed) > 6000:
            raise ValueError("Embed length is not 0-6000 characters long.")

        self.parent_view.embed = embed
        self.parent_view.update_counters()

        await interaction.edit_original_response(embed=embed, view=self.parent_view)
        await interaction.followup.send(content=f"{EMOJIS['yes']} - Embed imported from JSON",
            ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if isinstance(error, ValueError) or isinstance(error, discord.errors.HTTPException):
            await interaction.followup.send(content=f"{EMOJIS['no']} - Error: {str(error)}", ephemeral=True)
        elif isinstance(error, json.JSONDecodeError):
            await interaction.followup.send(f"{EMOJIS['no']} - Invalid JSON.",
                ephemeral=True)
        else:
            raise error


class ButtonMatrixView(TemporaryView):
    def __init__(self, buttons: ButtonMatrix, parent_view: EmbedBuilderView, original_button: DiscordButton = None):
        super().__init__()
        for i, button in enumerate([button for button in buttons]):
            if button is None:
                button = DiscordButton(button_struct=ButtonType.PICK_BUTTON,
                                    row=i // 5,
                                    index=i % 5,
                                    label=f"R {i // 5 + 1} C {i % 5 + 1}",
                                    style=discord.ButtonStyle.primary)
                button.parent_view = parent_view
                button.original_button = original_button
                button.matrix = buttons
            else:
                button.disabled = True
            self.add_item(button)

class EmbedBuilderView(BaseView):
    def __init__(self, *,
                 timeout: int,
                 target: discord.Interaction,
                 message: discord.Message,
                 embed: discord.Embed = None,
                 buttons: ButtonMatrix = []):
        self.message = message
        super().__init__(timeout=timeout, target=target)

        if embed is None:
            self.embed = discord.Embed()
        else:
            self.embed = embed
        self.buttons = buttons

    def update_counters(self):
        self.character_counter.label = f"{len(self.embed)}/6000 Characters"
        self.field_counter.label = f"{len(self.embed.fields)}/25 Fields"
        self.button_counter.label = f"{len(self.buttons)}/25 Buttons"

    @discord.ui.button(
        label="Edit:", style=discord.ButtonStyle.gray, disabled=True, row=0)
    async def _basic_tag(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="Embed", style=discord.ButtonStyle.primary, row=0)
    async def edit_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedModal(_embed=self.embed, parent_view=self))

    @discord.ui.button(label="Author", style=discord.ButtonStyle.primary, row=0)
    async def edit_author(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AuthorModal(_embed=self.embed, parent_view=self))

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.primary, row=0)
    async def edit_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FooterModal(_embed=self.embed, parent_view=self))

    @discord.ui.button(label="URL", style=discord.ButtonStyle.primary, row=0)
    async def edit_url(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(URLModal(_embed=self.embed, parent_view=self))

    @discord.ui.button(
        label="Fields:", style=discord.ButtonStyle.gray, disabled=True, row=1)
    async def _fields_tag(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(
        emoji=EMOJIS["white_plus"], style=discord.ButtonStyle.green, row=1)
    async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.embed.fields) == 25:
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed reached maximum of 25 fields.",
                ephemeral=True)
            return

        await interaction.response.send_modal(AddFieldModal(_embed=self.embed, parent_view=self))

    @discord.ui.button(
        emoji=EMOJIS["white_minus"], style=discord.ButtonStyle.red, row=1)
    async def delete_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.embed.fields) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - There are no fields to delete.", ephemeral=True)
        view = BaseView(timeout=180, target=interaction)
        view.add_item(DeleteFieldDropdown(_embed=self.embed, parent_view=self))
        await interaction.response.send_message(f"{EMOJIS['white_minus']} - Choose a field to delete:",
            view=view,
            ephemeral=True)

    @discord.ui.button(
        emoji=EMOJIS["white_pencil"], style=discord.ButtonStyle.primary, row=1)
    async def edit_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.embed.fields) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - There are no fields to edit.", ephemeral=True)

        view = BaseView(timeout=180, target=interaction)
        view.add_item(EditFieldDropdown(_embed=self.embed,
                                        parent_view=self))
        await interaction.response.send_message(f"{EMOJIS['white_pencil']} - Choose a field to edit:",
            view=view,
            ephemeral=True)

    @discord.ui.button(
        label="Buttons:", style=discord.ButtonStyle.gray, disabled=True, row=2)
    async def _buttons_tag(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji=EMOJIS["white_plus"], style=discord.ButtonStyle.green, row=2)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.buttons) == 25:
            await interaction.response.send_message(f"{EMOJIS['no']} - Embed reached maximum of 25 buttons.", ephemeral=True)
            return

        await interaction.response.send_message('Choose the button you\'d like to add',
                                                view=ButtonMatrixView(self.buttons, self),
                                                ephemeral=True)

    @discord.ui.button(emoji=EMOJIS["white_minus"], style=discord.ButtonStyle.red, row=2)
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.buttons) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - There are no buttons to delete.", ephemeral=True)
        view = BaseView(timeout=180, target=interaction)
        view.add_item(DeleteButtonDropdown(buttons=self.buttons, parent_view=self))
        await interaction.response.send_message(f"{EMOJIS['white_minus']} - Choose a button to delete:",
            view=view,
            ephemeral=True)

    @discord.ui.button(emoji=EMOJIS["white_pencil"], style=discord.ButtonStyle.primary, row=2)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.buttons) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - There are no buttons to edit.", ephemeral=True)

        view = BaseView(timeout=180, target=interaction)
        view.add_item(EditButtonDropdown(
            buttons=self.buttons,
            parent_view=self))
        await interaction.response.send_message(f"{EMOJIS['white_pencil']} - Choose a button to edit:",
            view=view,
            ephemeral=True)

    @discord.ui.button(emoji=EMOJIS["up_down_arrow"], style=discord.ButtonStyle.primary, row=2)
    async def move_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.buttons) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - There are no buttons to move.", ephemeral=True)

        view = BaseView(timeout=180, target=interaction)
        view.add_item(MoveButtonDropdown(
            buttons=self.buttons,
            parent_view=self))
        await interaction.response.send_message(f"{EMOJIS['white_pencil']} - Choose a button to move:",
            view=view,
            ephemeral=True)

    @discord.ui.button(label="Export JSON", style=discord.ButtonStyle.gray, row=3)
    async def export_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.embed) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - Embed is empty!", ephemeral=True)
        json_cont = json.dumps(self.embed.to_dict(), indent=4)
        stream = BytesIO(json_cont.encode())

        file = discord.File(fp=stream, filename="embed.json")
        await interaction.response.send_message(content="Here's your Embed as a JSON file:", file=file, ephemeral=True)

    @discord.ui.button(label="Import JSON", style=discord.ButtonStyle.gray, row=3)
    async def import_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ImportJSONModal(_embed=self.embed, parent_view=self))

    @discord.ui.button(label="Send to Channel", style=discord.ButtonStyle.green, row=3)
    async def send_to_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.embed) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - Embed is empty!", ephemeral=True)

        view = BaseView(timeout=180, target=interaction)
        view.add_item(SendToChannelSelect(_embed=self.embed, buttons=self.buttons))
        await interaction.response.send_message(f"{EMOJIS['channel_text']} - Choose a channel to send the embed to:",
            view=view,
            ephemeral=True)

    @discord.ui.button(label="Replace an embed", style=discord.ButtonStyle.green, row=3)
    async def replace_in_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.embed) == 0:
            return await interaction.response.send_message(f"{EMOJIS['no']} - Embed is empty!", ephemeral=True)

        view = BaseView(timeout=180, target=interaction)
        view.add_item(ReplaceChannelSelect(_embed=self.embed, buttons=self.buttons, parent_view=self))
        await interaction.response.send_message(f"{EMOJIS['channel_text']} - Choose a channel to send the embed to:",
            view=view,
            ephemeral=True)

    @discord.ui.button(
        label="0/6000 Characters",
        disabled=True,
        style=discord.ButtonStyle.gray,
        row=4)
    async def character_counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(
        label="0/25 Fields",
        disabled=True,
        style=discord.ButtonStyle.gray,
        row=4)
    async def field_counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(
        label="0/25 Buttons",
        disabled=True,
        style=discord.ButtonStyle.gray,
        row=4)
    async def button_counter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji=EMOJIS["white_x"], style=discord.ButtonStyle.red, row=4)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        await self.stop(interaction)
        await self.message.delete()