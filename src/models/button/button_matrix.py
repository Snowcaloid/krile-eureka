from data.db.sql import SQL, Batch, Record
from models.button import ButtonStruct
from models.button.discord_button import DiscordButton
from data_providers.buttons import ButtonsProvider
from ui.views import PersistentView, TemporaryView


from discord import Message
from discord.ui import View


from typing import List, Optional, Self, override
from uuid import uuid4


class ButtonMatrix(list[list[DiscordButton]]):
    def __init__(self, buttons: List[DiscordButton]):
        super().__init__([[None] * 5 for _ in range(5)]) # 5x5 matrix #type: ignore
        for button in buttons:
            self[button.struct.row][button.struct.index] = button

    def __len__(self):
        return sum(1 for elem in self if elem is not None)

    def __iter__(self):
        for row in super().__iter__():
            yield from row # Flatten

    @override
    def index(self, value: DiscordButton) -> int:
        for button in self:
            if button == value:
                return button.struct.row * 5 + button.struct.index
        return -1

    @classmethod
    def from_message(cls, message: Message) -> Self:
        result = []
        with Batch():
            for record in SQL('buttons').select(fields=['button_id'],
                                                where=f'message_id={message.id}',
                                                all=True):
                discord_button = DiscordButton(
                    ButtonsProvider().find(ButtonStruct(button_id=record['button_id']))
                )
                result.append(discord_button)
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