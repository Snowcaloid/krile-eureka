from __future__ import annotations
from abc import abstractmethod

from centralized_data import PythonAsset, PythonAssetLoader, Singleton
from discord.ext.commands import Bot
from discord.ui import Button, View
from discord import ButtonStyle, Emoji, Interaction, Message, PartialEmoji, Role, TextChannel
from typing import List, Optional, Tuple, Union, override
from basic_types import BUTTON_STYLE_DESCRIPTIONS, ButtonType
from data.db.sql import SQL, Record
from basic_types import BUTTON_TYPE_DESCRIPTIONS
from data.cache.message_cache import MessageCache

class ButtonTemplate(PythonAsset):
    @classmethod
    def base_asset_class_name(cls): return 'ButtonTemplate'

    @abstractmethod
    def button_type(self) -> ButtonType: ...

    @abstractmethod
    async def callback(self, interaction: Interaction, button: BaseButton): ...

class ButtonTemplates(PythonAssetLoader[ButtonTemplate]):
    @override
    def asset_folder_name(self) -> str:
        return 'buttons'

    def get(self, button_type: ButtonType) -> ButtonTemplate:
        return next(template for template in self.loaded_assets if template.button_type() == button_type)

class BaseButton(Button):
    @ButtonTemplates.bind
    def button_templates(self) -> ButtonTemplates: return ...

    def __init__(self,
                 button_type: ButtonType,
                 *,
                 style: ButtonStyle = ButtonStyle.secondary,
                 label: Optional[str] = None,
                 disabled: bool = False,
                 custom_id: Optional[str] = None,
                 url: Optional[str] = None,
                 emoji: Optional[Union[str, Emoji, PartialEmoji]] = None,
                 row: Optional[int] = None,
                 index: Optional[int] = None,
                 role: Optional[Role] = None,
                 pl: Optional[int] = None,
                 message: Optional[Message] = None,
                 event_id: Optional[int] = None):
        self.template: ButtonTemplate = self.button_templates.get(button_type)
        self.index: int = index
        self.role: Role = role
        self.pl: int = pl
        self.message: Message = message
        self.event_id: int = event_id
        super().__init__(style=style,label=label,disabled=disabled,custom_id=custom_id,url=url,row=row,emoji=emoji)

    @override
    async def callback(self, interaction: Interaction):
        if interaction.message == self.message:
            await self.template.callback(interaction, self)


def buttons_as_text(buttons: List[BaseButton]) -> str:
    buttons.sort(key=lambda btn: btn.row * 10 + btn.index)
    result = ''
    last_row = 0
    for button in buttons:
        newline = '\n' if last_row < button.row else ''
        color = BUTTON_STYLE_DESCRIPTIONS[button.style]
        type = BUTTON_TYPE_DESCRIPTIONS[button.template.button_type()]
        result = result + f'[ Button {button.emoji} "{button.label}" Color: "{color}" Type: "{type}" ]{newline}'
        last_row = button.row
    return result


def save_buttons(message: Message, view: View):
    query = Record() # Prevent multiple connects and disconnects
    for button in view.children:
        btn: BaseButton = button
        btn.message = message
        role = btn.role.id if btn.role else 0
        emoji = None if btn.emoji is None else str(btn.emoji)
        SQL('buttons').insert(Record(button_type=btn.template.button_type().value,
                                        style=btn.style.value,
                                        emoji=emoji,
                                        label=btn.label,
                                        button_id=btn.custom_id,
                                        row=btn.row,
                                        index=btn.index,
                                        role=role,
                                        pl=btn.pl,
                                        channel_id=message.channel.id,
                                        message_id=message.id,
                                        event_id=btn.event_id))
    del query


def delete_button(button_id: str) -> None:
    SQL('buttons').delete(f"button_id='{button_id}'")


def delete_buttons(message_id: str) -> None:
    SQL('buttons').delete(f'message_id={message_id}')


async def get_guild_button_data(button_id: str, channel_id: int, message_id: int, role_id: int) -> Tuple[Message, Role]:
    client = Singleton.get_instance(Bot)
    channel: TextChannel = client.get_channel(channel_id)
    if channel is None: channel = await client.fetch_channel(channel_id)
    if channel:
        message = await MessageCache().get(message_id, channel)
        if message:
            if role_id:
                role = channel.guild.get_role(role_id)
                if role:
                    return message, role
                else:
                    roles = await channel.guild.fetch_roles()
                    return message, next((role for role in roles if role.id == role_id), None)
            else:
                return message, None
        else:
            delete_button(button_id)
            return None, None
    else:
        delete_button(button_id)
        return None, None


async def load_button(button_id: str) -> BaseButton:
    for record in SQL('buttons').select(fields=['button_type', 'style', 'label',
                                                'row', 'index', 'role', 'pl',
                                                'channel_id', 'message_id', 'emoji', 'event_id'],
                                        where=f"button_id='{button_id}'",
                                        all=True):
        message, role = await get_guild_button_data(button_id, record['channel_id'], record['message_id'], record['role'])
        button = BaseButton(ButtonType(record['button_type']),
            style=ButtonStyle(record['style']),
            label=record['label'],
            custom_id=button_id,
            row=record['row'],
            index=record['index'],
            role=role,
            message=message,
            pl=record['pl'],
            emoji=record['emoji'],
            event_id=record['event_id']
        )
        return button
    return None

async def buttons_from_message(message: Message) -> List[BaseButton]:
    result = []
    query = Record() # Prevent multiple connects and disconnects
    for record in SQL('buttons').select(fields=['button_id'],
                                        where=f'message_id={message.id}',
                                        all=True):
        result.append(await load_button(record[0]))
    del query
    return result