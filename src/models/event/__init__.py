from __future__ import annotations
from datetime import datetime
from typing import List, override
from bot import Bot
from models._base import BaseStruct
from utils.basic_types import Unassigned

from dataclasses import dataclass


PL_FIELDS = ['pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'pl6', 'pls']

@dataclass
class EventStruct(BaseStruct):
    guild_id: int = Unassigned
    id: int = Unassigned
    event_type: str = Unassigned
    timestamp: datetime = Unassigned
    custom_description: str = Unassigned
    raid_leader_id: int = Unassigned
    party_leader_ids: List[int] = Unassigned
    use_support: bool = Unassigned
    passcode_main: int = Unassigned
    passcode_support: int = Unassigned
    recruitment_post_id: int = Unassigned
    finished: bool = Unassigned
    canceled: bool = Unassigned
    is_signup: bool = Unassigned

    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def __eq__(self, other: EventStruct) -> bool:
        return self.id == other.id

    @override
    def __repr__(self) -> str:
        result = []
        if self.guild_id is not None:
            result.append(f"Guild ID: {self.guild_id}")
        if self.id is not None:
            result.append(f"Event ID: {self.id}")
        if self.event_type is not None:
            result.append(f"Event Type: {self.event_type}")
        if self.timestamp is not None:
            result.append(f"Timestamp: {self.timestamp}")
        if self.custom_description is not None:
            result.append(f"Description: {self.custom_description}")
        if self.raid_leader_id is not None:
            result.append(f"Raid Leader ID: {self.raid_leader_id}")
        if self.party_leader_ids:
            result.append(f"Party Leaders: {', '.join([
                self._bot.client.get_user(id).display_name for id in self.party_leader_ids if id is not None])}")
        if self.use_support is not None:
            result.append(f"Use Support: {self.use_support}")
        if self.passcode_main is not None:
            result.append(f"Main Passcode: {self.passcode_main}")
        if self.passcode_support is not None:
            result.append(f"Support Passcode: {self.passcode_support}")
        if self.recruitment_post_id is not None:
            result.append(f"Recruitment Post ID: {self.recruitment_post_id}")
        if self.finished is not None:
            result.append(f"Finished: {self.finished}")
        if self.canceled is not None:
            result.append(f"Canceled: {self.canceled}")
        if self.is_signup is not None:
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
            result.append(f"Timestamp: {other.timestamp} -> {self.timestamp}.")
        if self.custom_description != other.custom_description:
            result.append(f"Description: {other.custom_description} -> {self.custom_description}.")
        if self.raid_leader_id != other.raid_leader_id:
            result.append(f"Raid Leader ID: {other.raid_leader_id} -> {self.raid_leader_id}.")
        if self.party_leader_ids != other.party_leader_ids:
            result.append(f"Party Leaders: {', '.join([
                self._bot.client.get_user(id).display_name for id in other.party_leader_ids if id is not None])} "
                          f"-> {', '.join([
                self._bot.client.get_user(id).display_name for id in self.party_leader_ids if id is not None])}.")
        if self.use_support != other.use_support:
            result.append(f"Use Support: {other.use_support} -> {self.use_support}.")
        if self.passcode_main != other.passcode_main:
            result.append(f"Main Passcode: {other.passcode_main} -> {self.passcode_main}.")
        if self.passcode_support != other.passcode_support:
            result.append(f"Support Passcode: {other.passcode_support} -> {self.passcode_support}.")
        if self.recruitment_post_id != other.recruitment_post_id:
            result.append(f"Recruitment Post ID: {other.recruitment_post_id} -> {self.recruitment_post_id}.")
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
            'custom_description': self.custom_description,
            'raid_leader_id': self.raid_leader_id,
            'party_leader_ids': self.party_leader_ids,
            'use_support': self.use_support,
            'passcode_main': self.passcode_main,
            'passcode_support': self.passcode_support,
            'recruitment_post_id': self.recruitment_post_id,
            'finished': self.finished,
            'canceled': self.canceled,
            'is_signup': self.is_signup
        }