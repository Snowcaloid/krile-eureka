from __future__ import annotations

from discord.ui import View
from discord import ButtonStyle, Message, Role, TextChannel
from typing import Tuple
from models.button.discord_button import DiscordButton
from utils.basic_types import ButtonType
from bot import Bot
from data.db.sql import SQL, Record
from data.cache.message_cache import MessageCache

# TODO: ButtonsService
def save_buttons(message: Message, view: View):
    query = Record() # Prevent multiple connects and disconnects
    for button in view.children:
        btn: DiscordButton = button
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
