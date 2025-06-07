from __future__ import annotations
from datetime import datetime
from typing import override
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
    description: str = Unassigned
    raid_leader: int = Unassigned
    pl1: int = Unassigned
    pl2: int = Unassigned
    pl3: int = Unassigned
    pl4: int = Unassigned
    pl5: int = Unassigned
    pl6: int = Unassigned
    pls: int = Unassigned
    use_support: bool = Unassigned
    pass_main: int = Unassigned
    pass_supp: int = Unassigned
    pl_post_id: int = Unassigned
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
        if self.description is not None:
            result.append(f"Description: {self.description}")
        if self.raid_leader is not None:
            result.append(f"Raid Leader: {self._bot.client.get_user(self.raid_leader).mention}")
        if self.pl1 is not None:
            result.append(f"Party Leader 1: {self._bot.client.get_user(self.pl1).mention}")
        if self.pl2 is not None:
            result.append(f"Party Leader 2: {self._bot.client.get_user(self.pl2).mention}")
        if self.pl3 is not None:
            result.append(f"Party Leader 3: {self._bot.client.get_user(self.pl3).mention}")
        if self.pl4 is not None:
            result.append(f"Party Leader 4: {self._bot.client.get_user(self.pl4).mention}")
        if self.pl5 is not None:
            result.append(f"Party Leader 5: {self._bot.client.get_user(self.pl5).mention}")
        if self.pl6 is not None:
            result.append(f"Party Leader 6: {self._bot.client.get_user(self.pl6).mention}")
        if self.pls is not None and self.use_support:
            result.append(f"Support Leader: {self._bot.client.get_user(self.pls).mention}")
        if self.use_support is not None:
            result.append(f"Use Support: {self.use_support}")
        if self.pass_main is not None:
            result.append(f"Main Passcode: {self.pass_main}")
        if self.pass_supp is not None:
            result.append(f"Support Passcode: {self.pass_supp}")
        if self.pl_post_id is not None:
            result.append(f"Recruitment Post ID: {self.pl_post_id}")
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
            result.append(f"Timestamp: {other.timestamp.strftime("%d-%m-%Y% %H:%M ST")} -> {self.timestamp.strftime("%d-%m-%Y% %H:%M ST")}.")
        if self.description != other.description:
            result.append(f"Description: {other.description} -> {self.description}.")
        if self.raid_leader != other.raid_leader:
            result.append(f"Raid Leader: {
                          self._bot.client.get_user(other.raid_leader).mention } -> {
                          self._bot.client.get_user(self.raid_leader).mention}.")
        if self.pl1 != other.pl1:
            result.append(f"Party Leader 1: {
                self._bot.client.get_user(other.pl1).mention if other.pl1 is not None else "None"} -> {
                self._bot.client.get_user(self.pl1).mention if self.pl1 is not None else "None"}.")
        if self.pl2 != other.pl2:
            result.append(f"Party Leader 2: {
                self._bot.client.get_user(other.pl2).mention if other.pl2 is not None else "None"} -> {
                self._bot.client.get_user(self.pl2).mention if self.pl2 is not None else "None"}.")
        if self.pl3 != other.pl3:
            result.append(f"Party Leader 3: {
                self._bot.client.get_user(other.pl3).mention if other.pl3 is not None else "None"} -> {
                self._bot.client.get_user(self.pl3).mention if self.pl3 is not None else "None"}.")
        if self.pl4 != other.pl4:
            result.append(f"Party Leader 4: {
                self._bot.client.get_user(other.pl4).mention if other.pl4 is not None else "None"} -> {
                self._bot.client.get_user(self.pl4).mention if self.pl4 is not None else "None"}.")
        if self.pl5 != other.pl5:
            result.append(f"Party Leader 5: {
                self._bot.client.get_user(other.pl5).mention if other.pl5 is not None else "None"} -> {
                self._bot.client.get_user(self.pl5).mention if self.pl5 is not None else "None"}.")
        if self.pl6 != other.pl6:
            result.append(f"Party Leader 6: {
                self._bot.client.get_user(other.pl6).mention if other.pl6 is not None else "None"} -> {
                self._bot.client.get_user(self.pl6).mention if self.pl6 is not None else "None"}.")
        if self.pls != other.pls and \
           (self.use_support or ((self.use_support is None or self.use_support is Unassigned) and \
                                 other.use_support)):
            result.append(f"Support Leader: {
                self._bot.client.get_user(other.pls).mention if other.pls is not None else "None"} -> {
                self._bot.client.get_user(self.pls).mention if self.pls is not None else "None"}.")
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
            'raid_leader_id': {
                'id': self.raid_leader,
                'name': self._bot.client.get_guild(self.guild_id).get_user(self.raid_leader).display_name if self.raid_leader else None
            },
            'party_leaders': [
                {
                    'id': pl,
                    'name': self._bot.client.get_guild(self.guild_id).get_user(pl).display_name
                } if pl else None
                for pl in [self.pl1, self.pl2, self.pl3, self.pl4, self.pl5, self.pl6]
            ],
            'use_support': self.use_support,
            'passcode_main': self.pass_main,
            'passcode_support': self.pass_supp,
            'recruitment_post_id': self.pl_post_id,
            'finished': self.finished,
            'canceled': self.canceled,
            'is_signup': self.is_signup
        }