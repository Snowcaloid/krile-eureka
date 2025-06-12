from __future__ import annotations
from datetime import datetime
from typing import override
from models._base import BaseStruct
from utils.basic_types import Unassigned

from dataclasses import dataclass

from utils.functions import is_null_or_unassigned


@dataclass
class EventStruct(BaseStruct):
    guild_id: int = Unassigned
    id: int = Unassigned
    event_type: str = Unassigned
    timestamp: datetime = Unassigned
    description: str = Unassigned
    use_support: bool = Unassigned
    pass_main: int = Unassigned
    pass_supp: int = Unassigned
    pl_post_id: int = Unassigned
    finished: bool = Unassigned
    canceled: bool = Unassigned
    is_signup: bool = Unassigned

    @override
    def __eq__(self, other: EventStruct) -> bool:
        return self.id == other.id

    @override
    def __repr__(self) -> str:
        result = []
        if not is_null_or_unassigned(self.guild_id):
            result.append(f"Guild ID: {self.guild_id}")
        if not is_null_or_unassigned(self.id):
            result.append(f"Event ID: {self.id}")
        if not is_null_or_unassigned(self.event_type):
            result.append(f"Event Type: {self.event_type}")
        if not is_null_or_unassigned(self.timestamp):
            result.append(f"Timestamp: {self.timestamp}")
        if not is_null_or_unassigned(self.description):
            result.append(f"Description: {self.description}")
        if not is_null_or_unassigned(self.raid_leader):
            result.append(f"Raid Leader: {self._bot.client.get_user(self.raid_leader).mention}")
        if not is_null_or_unassigned(self.use_support):
            result.append(f"Use Support: {self.use_support}")
        if not is_null_or_unassigned(self.pass_main):
            result.append(f"Main Passcode: {self.pass_main}")
        if not is_null_or_unassigned(self.pass_supp):
            result.append(f"Support Passcode: {self.pass_supp}")
        if not is_null_or_unassigned(self.pl_post_id):
            result.append(f"Recruitment Post ID: {self.pl_post_id}")
        if not is_null_or_unassigned(self.finished):
            result.append(f"Finished: {self.finished}")
        if not is_null_or_unassigned(self.canceled):
            result.append(f"Canceled: {self.canceled}")
        if not is_null_or_unassigned(self.is_signup):
            result.append(f"Is Signup: {self.is_signup}")
        return

    @override
    def changes_since(self, other: EventStruct) -> str:
        result = []
        if self.guild_id != other.guild_id:
            result.append(f"Guild ID: {other.guild_id} -> {self.guild_id}.")
        if self.id != other.id:
            result.append(f"Event ID: {other.id} -> {self.id}.")
        if self.event_type != other.event_type:
            result.append(f"Event Type: {other.event_type} -> {self.event_type}.")
        if self.timestamp != other.timestamp:
            result.append(f"Timestamp: {other.timestamp.strftime("%d-%m-%Y% %H:%M ST")} -> {self.timestamp.strftime("%d-%m-%Y% %H:%M ST")}.")
        if self.description != other.description:
            result.append(f"Description: {other.description} -> {self.description}.")
        if self.raid_leader != other.raid_leader:
            result.append(f"Raid Leader: {
                          self._bot.client.get_user(other.raid_leader).mention } -> {
                          self._bot.client.get_user(self.raid_leader).mention}.")
        if self.use_support != other.use_support:
            result.append(f"Use Support: {other.use_support} -> {self.use_support}.")
        if self.pass_main != other.pass_main:
            result.append(f"Main Passcode: {other.pass_main} -> {self.pass_main}.")
        if self.pass_supp != other.pass_supp:
            result.append(f"Support Passcode: {other.pass_supp} -> {self.pass_supp}.")
        if self.pl_post_id != other.pl_post_id:
            result.append(f"Recruitment Post ID: {other.pl_post_id} -> {self.pl_post_id}.")
        if self.finished != other.finished:
            result.append(f"Finished: {other.finished} -> {self.finished}.")
        if self.canceled != other.canceled:
            result.append(f"Canceled: {other.canceled} -> {self.canceled}.")
        if self.is_signup != other.is_signup:
            result.append(f"Is Signup: {other.is_signup} -> {self.is_signup}.")
        if not result:
            result.append("No changes.")
        return result

    def marshal(self) -> dict:
        return {
            'guild_id': self.guild_id,
            'id': self.id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'custom_description': self.description,
            'raid_leader': {
                'id': self.raid_leader,
                'name': self._bot.client.get_guild(self.guild_id).get_user(self.raid_leader).display_name if self.raid_leader else None
            },
            'use_support': self.use_support,
            'passcode_main': self.pass_main,
            'passcode_support': self.pass_supp,
            'recruitment_post_id': self.pl_post_id,
            'finished': self.finished,
            'canceled': self.canceled,
            'is_signup': self.is_signup
        }