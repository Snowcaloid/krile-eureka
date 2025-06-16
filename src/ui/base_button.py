from __future__ import annotations

from discord.ui import View
from discord import Message
from models.button.discord_button import DiscordButton
from data.db.sql import Record, Transaction

# TODO: ButtonsWriter
def save_buttons(message: Message, view: View):
    with Transaction() as transaction:
        for button in view.children:
            btn: DiscordButton = button # type: ignore
            transaction.sql('buttons').insert(Record(button_type=btn.template.button_type().value,
                                                     style=btn.style.value,
                                                     emoji=btn.struct.emoji,
                                                     label=btn.label,
                                                     button_id=btn.custom_id,
                                                     row=btn.row,
                                                     index=btn.struct.index,
                                                     role=btn.struct.role_id,
                                                     pl=btn.struct.party,
                                                     channel_id=message.channel.id,
                                                     message_id=message.id,
                                                     event_id=btn.struct.event_id))


def delete_button(button_id: str) -> None:
    with Transaction() as transaction:
        transaction.sql('buttons').delete(f"button_id='{button_id}'")


def delete_buttons(message_id: str) -> None:
    with Transaction() as transaction:
        transaction.sql('buttons').delete(f'message_id={message_id}')
