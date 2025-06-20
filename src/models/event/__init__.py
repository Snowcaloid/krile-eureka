from __future__ import annotations
from datetime import datetime
from typing import override
from models._base import BaseStruct
from utils.basic_types import Unassigned

from dataclasses import dataclass


@dataclass
class EventStruct(BaseStruct):
    id: int = Unassigned #type: ignore
    guild_id: int = Unassigned #type: ignore
    guild_name: str = Unassigned #type: ignore
    event_type: str = Unassigned #type: ignore
    timestamp: datetime = Unassigned #type: ignore
    custom_description: str = Unassigned #type: ignore
    raid_leader: int = Unassigned #type: ignore
    raid_leader_name: str = Unassigned #type: ignore
    disable_support: bool = Unassigned #type: ignore
    passcode_main: int = Unassigned #type: ignore
    passcode_support: int = Unassigned #type: ignore
    recruitment_post_id: int = Unassigned #type: ignore
    finished: bool = Unassigned #type: ignore
    canceled: bool = Unassigned #type: ignore
    is_signup: bool = Unassigned #type: ignore

    @classmethod
    def db_table_name(cls) -> str:
        return 'events'

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def fixup_types(self) -> None: ...

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.guild_id, int):
            result.append(f'Guild ID: {self.guild_id}')
        if isinstance(self.guild_name, int):
            result.append(f'Guild Name: {self.guild_name}')
        if isinstance(self.id, str):
            result.append(f'Event ID: {self.id}')
        if isinstance(self.event_type, str):
            result.append(f'Event Type: {self.event_type}')
        if isinstance(self.timestamp, datetime):
            result.append(f'Timestamp: {self.timestamp}')
        if isinstance(self.custom_description, str):
            result.append(f'Description: {self.custom_description}')
        if isinstance(self.raid_leader, int):
            result.append(f'Raid Leader: {self._bot.get_user(self.raid_leader).mention}')
        if isinstance(self.raid_leader_name, str):
            result.append(f'Raid Leader Name: {self.raid_leader_name}')
        if isinstance(self.disable_support, bool):
            result.append(f'Support disabled: {self.disable_support}')
        if isinstance(self.passcode_main, int):
            result.append(f'Main Passcode: {self.passcode_main}')
        if isinstance(self.passcode_support, int):
            result.append(f'Support Passcode: {self.passcode_support}')
        if isinstance(self.recruitment_post_id, int):
            result.append(f'Recruitment Post ID: {self.recruitment_post_id}')
        if isinstance(self.finished, bool):
            result.append(f'Finished: {self.finished}')
        if isinstance(self.canceled, bool):
            result.append(f'Canceled: {self.canceled}')
        if isinstance(self.is_signup, bool):
            result.append(f'Is Signup: {self.is_signup}')
        return 'EventStruct(' + ', '.join(result) + ')' if result else 'No event data available.'

    @override
    def changes_since(self, other: EventStruct) -> str:
        result = []
        if isinstance(self.guild_id, int) and self.guild_id != other.guild_id:
            result.append(f'  Guild ID: {other.guild_id} -> {self.guild_id}.')
        if isinstance(self.guild_name, int) and self.guild_name != other.guild_name:
            result.append(f'  Guild Name: {other.guild_name} -> {self.guild_name}.')
        if isinstance(self.id, str) and self.id != other.id:
            result.append(f'  Event ID: {other.id} -> {self.id}.')
        if isinstance(self.event_type, str) and self.event_type != other.event_type:
            result.append(f'  Event Type: {other.event_type} -> {self.event_type}.')
        if isinstance(self.timestamp, datetime) and self.timestamp != other.timestamp:
            result.append(f'  Timestamp: {other.timestamp.strftime('%d-%m-%Y% %H:%M ST')} -> {self.timestamp.strftime('%d-%m-%Y% %H:%M ST')}.')
        if isinstance(self.custom_description, str) and self.custom_description != other.custom_description:
            result.append(f'  Description: {other.custom_description} -> {self.custom_description}.')
        if isinstance(self.raid_leader, int) and self.raid_leader != other.raid_leader:
            result.append(f'  Raid Leader ID: {other.raid_leader} -> {self.raid_leader}.')
        if isinstance(self.raid_leader_name, str) and self.raid_leader_name != other.raid_leader_name:
            result.append(f'  Raid Leader Name: {other.raid_leader_name} -> {self.raid_leader_name}.')
        if isinstance(self.disable_support, bool) and self.disable_support != other.disable_support:
            result.append(f'  Support disabled: {other.disable_support} -> {self.disable_support}.')
        if isinstance(self.passcode_main, int) and self.passcode_main != other.passcode_main:
            result.append(f'  Main Passcode: {other.passcode_main} -> {self.passcode_main}.')
        if isinstance(self.passcode_support, int) and self.passcode_support != other.passcode_support:
            result.append(f'  Support Passcode: {other.passcode_support} -> {self.passcode_support}.')
        if isinstance(self.recruitment_post_id, int) and self.recruitment_post_id != other.recruitment_post_id:
            result.append(f'  Recruitment Post ID: {other.recruitment_post_id} -> {self.recruitment_post_id}.')
        if isinstance(self.finished, bool) and self.finished != other.finished:
            result.append(f'  Finished: {other.finished} -> {self.finished}.')
        if isinstance(self.canceled, bool) and self.canceled != other.canceled:
            result.append(f'  Canceled: {other.canceled} -> {self.canceled}.')
        if isinstance(self.is_signup, bool) and self.is_signup != other.is_signup:
            result.append(f'  Is Signup: {other.is_signup} -> {self.is_signup}.')
        if not result:
            result.append('  No changes.')
        return '\n'.join(result)

    def marshal(self) -> dict:
        return {
            'guild': {
                'id': self.marshal_value(self.guild_id),
                'name': self.marshal_value(self.guild_name)
            },
            'id': self.marshal_value(self.id),
            'event_type': self.marshal_value(self.event_type),
            'timestamp': self.marshal_value(self.timestamp),
            'custom_description': self.marshal_value(self.custom_description),
            'raid_leader': {
                'id': self.marshal_value(self.raid_leader),
                'name': self.marshal_value(self.raid_leader_name)
            },
            'disable_support': self.marshal_value(self.disable_support),
            'passcode_main': self.marshal_value(self.passcode_main),
            'passcode_support': self.marshal_value(self.passcode_support),
            'recruitment_post_id': self.marshal_value(self.recruitment_post_id),
            'is_signup': self.marshal_value(self.is_signup),
            'finished': self.marshal_value(self.finished),
            'canceled': self.marshal_value(self.canceled)
        }