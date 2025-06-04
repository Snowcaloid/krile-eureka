from __future__ import annotations
from dataclasses import dataclass
from typing import override

from discord import ButtonStyle
from models._base import BaseStruct
from utils.basic_types import ButtonType, Unassigned, fix_enum

@dataclass
class ButtonStruct(BaseStruct):
    button_id: str = Unassigned
    button_type: ButtonType = Unassigned
    channel_id: int = Unassigned
    message_id: int = Unassigned
    emoji: str = Unassigned
    label: str = Unassigned
    style: ButtonStyle = Unassigned
    row: int = Unassigned
    index: int = Unassigned
    role_id: int = Unassigned
    party: int = Unassigned
    event_id: int = Unassigned

    @override
    def fixup_enums(self) -> None:
        self.button_type = fix_enum(ButtonType, self.button_type)
        self.style = fix_enum(ButtonStyle, self.style)