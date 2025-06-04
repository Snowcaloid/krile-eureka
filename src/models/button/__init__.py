from __future__ import annotations
from dataclasses import dataclass
from typing import override

from discord import Button, ButtonStyle
from data.db.sql import Record
from models._base import BaseStruct
from utils.basic_types import ButtonType

@dataclass
class ButtonStruct(BaseStruct):
    button_id: str = None
    button_type: ButtonType
    channel_id: int = None
    message_id: int = None
    emoji: str = None
    label: str = None
    style: ButtonStyle = None
    row: int = None
    index: int = None
    role_id: int = None
    party: int = None
    event_id: int = None
