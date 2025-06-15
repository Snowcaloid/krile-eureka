from __future__ import annotations
from typing import override
from models._base import BaseStruct
from utils.basic_types import Unassigned

from dataclasses import dataclass

from utils.functions import is_null_or_unassigned


@dataclass
class EventUserStruct(BaseStruct):
    id: int = Unassigned
    event_id: int = Unassigned
    user_id: int = Unassigned
    user_name: str = Unassigned
    is_party_leader: bool = Unassigned
    party: int = Unassigned
    slot: int = Unassigned
    slot_name: str = Unassigned

    @classmethod
    def db_table_name(cls) -> str:
        return 'event_users'

    @override
    def __repr__(self) -> str:
        result = []
        if not is_null_or_unassigned(self.id):
            result.append(f"ID: {self.id}")
        if not is_null_or_unassigned(self.event_id):
            result.append(f"Event ID: {self.event_id}")
        if not is_null_or_unassigned(self.user_id):
            result.append(f"User ID: {self.user_id}")
        if not is_null_or_unassigned(self.user_name):
            result.append(f"User Name: {self.user_name}")
        if not is_null_or_unassigned(self.is_party_leader):
            result.append(f"Is Party Leader: {self.is_party_leader}")
        if not is_null_or_unassigned(self.party):
            result.append(f"Party: {self.party}")
        if not is_null_or_unassigned(self.slot):
            result.append(f"Slot: {self.slot}")
        if not is_null_or_unassigned(self.slot_name):
            result.append(f"Slot Name: {self.slot_name}")
        return ', '.join(result)

    @override
    def changes_since(self, other: EventUserStruct) -> str:
        result = []
        if self.event_id != other.event_id:
            result.append(f"Event ID: {other.event_id} -> {self.event_id}.")
        if self.user_id != other.user_id:
            result.append(f"User ID: {other.user_id} -> {self.user_id}.")
        if self.user_name != other.user_name:
            result.append(f"User Name: {other.user_name} -> {self.user_name}.")
        if self.is_party_leader != other.is_party_leader:
            result.append(f"Is Party Leader: {other.is_party_leader} -> {self.is_party_leader}.")
        if self.party != other.party:
            result.append(f"Party: {other.party} -> {self.party}.")
        if self.slot != other.slot:
            result.append(f"Slot: {other.slot} -> {self.slot}.")
        if self.slot_name != other.slot_name:
            result.append(f"Slot Name: {other.slot_name} -> {self.slot_name}.")
        if not result:
            result.append("No changes.")
        return ', '.join(result)

    def marshal(self) -> dict:
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user': {
                'id': self.user_id,
                'name': self.user_name
            },
            'is_party_leader': self.is_party_leader,
            'party': self.party,
            'slot': self.slot,
            'slot_name': self.slot_name
        }