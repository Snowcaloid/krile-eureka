from __future__ import annotations
from abc import abstractmethod
from uuid import uuid4

from centralized_data import PythonAsset, PythonAssetLoader
from discord.ui import Button, View
from discord import ButtonStyle, Emoji, Interaction, Message, PartialEmoji, Role, TextChannel
from typing import List, Optional, Self, Tuple, Union, override
from utils.basic_types import ButtonType
from bot import Bot
from data.db.sql import SQL, Record
from data.cache.message_cache import MessageCache
from data.ui.views import PersistentView, TemporaryView

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
        if self.message is None or interaction.message == self.message:
            await self.template.callback(interaction, self)

class ButtonMatrix(list[BaseButton]):
    def __init__(self, buttons: List[BaseButton]):
        super().__init__([[None] * 5 for _ in range(5)]) # 5x5 matrix
        for button in buttons:
            self[button.row][button.index] = button

    def __len__(self):
        return sum(1 for elem in self if elem is not None)

    def __iter__(self):
        for row in super().__iter__():
            yield from row # Flatten

    @override
    def index(self, value: BaseButton) -> int:
        for button in self:
            if button == value:
                return button.row * 5 + button.index
        return -1

    @classmethod
    async def from_message(cls, message: Message) -> Self:
        result = []
        query = Record() # Prevent multiple connects and disconnects
        for record in SQL('buttons').select(fields=['button_id'],
                                            where=f'message_id={message.id}',
                                            all=True):
            result.append(await load_button(record["button_id"]))
        del query
        return cls(result)

    @property
    def disabled(self) -> bool:
        return all(button is None or button.disabled for button in self)

    @disabled.setter
    def disabled(self, value: bool):
        for button in self:
            if button is not None:
                button.disabled = value

    def as_view(self, persistent: bool = False) -> View:
        if persistent:
            view = PersistentView()
            self.disabled = False
        else:
            view = TemporaryView()
        for button in self:
            if button is not None:
                if button.custom_id is None:
                    button.custom_id = str(uuid4())
                view.add_item(button)
        return view

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
    client = Bot().client
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
