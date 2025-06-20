from __future__ import annotations
from typing import override
from bot import Bot
from models._base import BaseStruct
from utils.basic_types import EurekaInstance, RoleDenominator, RoleFunction, NotoriousMonster, EventCategory, Unassigned

from dataclasses import dataclass

from utils.functions import fix_enum


@dataclass
class RoleAssignmentStruct(BaseStruct):
    id: int = Unassigned #type: ignore
    guild_id: int = Unassigned #type: ignore
    guild_name: str = Unassigned #type: ignore
    role_id: int = Unassigned #type: ignore
    role_name: str = Unassigned #type: ignore
    function: RoleFunction = Unassigned #type: ignore
    denominator: RoleDenominator = Unassigned #type: ignore
    event_type: str = Unassigned #type: ignore
    event_category: EventCategory = Unassigned #type: ignore
    notorious_monster: NotoriousMonster = Unassigned #type: ignore
    eureka_instance: EurekaInstance = Unassigned #type: ignore

    @Bot.bind
    def _bot(self) -> Bot: ...

    @classmethod
    def db_table_name(cls) -> str:
        return 'roles'

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(RoleFunction, self.function)
        assert isinstance(fixed_enum, RoleFunction), f"Invalid RoleFunction: {self.function}"
        self.function = fixed_enum
        fixed_enum = fix_enum(RoleDenominator, self.denominator)
        assert isinstance(fixed_enum, RoleDenominator), f"Invalid RoleDenominator: {self.denominator}"
        self.denominator = fixed_enum
        fixed_enum = fix_enum(NotoriousMonster, self.notorious_monster)
        assert isinstance(fixed_enum, NotoriousMonster), f"Invalid NotoriousMonster: {self.notorious_monster}"
        self.notorious_monster = fixed_enum
        fixed_enum = fix_enum(EurekaInstance, self.eureka_instance)
        assert isinstance(fixed_enum, EurekaInstance), f"Invalid EurekaInstance: {self.eureka_instance}"
        self.eureka_instance = fixed_enum

    @override
    def __repr__(self) -> str:
        result = []
        if self.guild_id is not None:
            result.append(f"Guild ID: {self.guild_id}")
        if self.id is not None:
            result.append(f"ID: {self.id}")
        if self.role_id is not None:
            role_name = self._bot.get_role(self.guild_id, self.role_id).name if self.role_id else 'Unknown'
            result.append(f"Role: @{role_name} ({str(self.role_id)})")
        if self.event_category is not None:
            result.append(f"Event Type: {self.event_category}")
        if self.function is not None:
            result.append(f"Function: {self.function.name}")
        return ', '.join(result)

    @override
    def changes_since(self, other: RoleAssignmentStruct) -> str:
        result = []
        if other.id != self.id:
            result.append(f"ID: {other.id} -> {self.id}")
        if other.role_id != self.role_id:
            role_name = self._bot.get_role(self.guild_id, self.role_id).name if self.role_id else 'Unknown'
            other_role_name = self._bot.get_role(other.guild_id, other.role_id).name if other.role_id else 'Unknown'
            result.append(f"Role: @{other_role_name} ({str(other.role_id)}) -> #{role_name} ({str(self.role_id)})")
        if other.event_category != self.event_category:
            result.append(f"Event Type: {other.event_category} -> {self.event_category}")
        if other.function != self.function:
            result.append(f"Function: {other.function.name} -> {self.function.name}")
        if not result:
            return "No changes"

    def marshal(self) -> dict:
        return {
            'guild_id': str(self.guild_id),
            'id': str(self.id),
            'role': {
                'id': str(self.role_id),
                'name': self._bot.get_role(self.guild_id, self.role_id).name
            },
            'event_category': self.event_category,
            'function': self.function.name
        }