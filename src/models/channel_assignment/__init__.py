from __future__ import annotations
from dataclasses import dataclass
from typing import override
from bot import Bot
from data.events.event_category import EventCategory
from models._base import BaseStruct
from utils.basic_types import EurekaInstance, NotoriousMonster, Unassigned, ChannelFunction, fix_enum, ChannelDenominator


@dataclass
class ChannelAssignmentStruct(BaseStruct):
    guild_id: int = Unassigned #type: ignore
    id: int = Unassigned #type: ignore
    channel_id: int = Unassigned #type: ignore
    event_type: str = Unassigned #type: ignore
    function: ChannelFunction = Unassigned #type: ignore
    denominator: ChannelDenominator = Unassigned #type: ignore
    event_category: EventCategory = Unassigned #type: ignore
    notorious_monster: NotoriousMonster = Unassigned #type: ignore
    eureka_instance: EurekaInstance = Unassigned #type: ignore
    eureka_instance_name: str = Unassigned #type: ignore

    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def fixup_types(self) -> None:
        fixed_enum = fix_enum(ChannelFunction, self.function)
        assert isinstance(fixed_enum, ChannelFunction), f"Invalid GuildChannelFunction: {self.function}"
        self.function = fixed_enum
        fixed_enum = fix_enum(ChannelDenominator, self.denominator)
        assert isinstance(fixed_enum, ChannelDenominator), f"Invalid GuildChannelDenominator: {self.denominator}"
        self.denominator = fixed_enum
        fixed_enum = fix_enum(EventCategory, self.event_category)
        assert isinstance(fixed_enum, EventCategory), f"Invalid EventCategory: {self.event_category}"
        self.event_category = fixed_enum
        fixed_enum = fix_enum(NotoriousMonster, self.notorious_monster)
        assert isinstance(fixed_enum, NotoriousMonster), f"Invalid NotoriousMonster: {self.notorious_monster}"
        self.notorious_monster = fixed_enum
        fixed_enum = fix_enum(EurekaInstance, self.eureka_instance)
        assert isinstance(fixed_enum, EurekaInstance), f"Invalid EurekaTrackerZone: {self.eureka_instance}"
        self.eureka_instance = fixed_enum

    @override
    def __repr__(self) -> str:
        result = []
        if isinstance(self.guild_id, int):
            result.append(f"Guild ID: {self.guild_id}")
        if isinstance(self.id, int):
            result.append(f"ID: {self.id}")
        if isinstance(self.channel_id, int):
            channel_name = self._bot.get_text_channel(self.channel_id).name if self.channel_id else 'Unknown'
            result.append(f"Channel: #{channel_name} ({str(self.channel_id)})")
        if isinstance(self.event_type, str):
            result.append(f"Event Type: {self.event_type}")
        if isinstance(self.function, ChannelFunction):
            result.append(f"Function: {self.function.name}")
        if isinstance(self.denominator, ChannelDenominator):
            result.append(f"Denominator: {self.denominator.name}")
        if isinstance(self.event_category, EventCategory):
            result.append(f"Event Category: {self.event_category.name}")
        if isinstance(self.notorious_monster, NotoriousMonster):
            result.append(f"Notorious Monster: {self.notorious_monster.name}")
        if isinstance(self.eureka_instance, EurekaInstance):
            result.append(f"Eureka Instance: {self.eureka_instance.name} ({self.eureka_instance.value})")
        return ', '.join(result)

    @override
    def changes_since(self, other: ChannelAssignmentStruct) -> str:
        result = []
        if isinstance(self.id, int) and other.id != self.id:
            result.append(f"ID: {other.id} -> {self.id}")
        if isinstance(self.channel_id, int) and other.channel_id != self.channel_id:
            channel_name = self._bot.get_text_channel(self.channel_id).name if self.channel_id else 'Unknown'
            other_channel_name = self._bot.get_text_channel(other.channel_id).name if other.channel_id else 'Unknown'
            result.append(f"Channel: #{other_channel_name} ({str(other.channel_id)}) -> #{channel_name} ({str(self.channel_id)})")
        if isinstance(self.event_type, str) and other.event_type != self.event_type:
            result.append(f"Event Type: {other.event_type} -> {self.event_type}")
        if isinstance(self.function, ChannelFunction) and other.function != self.function:
            result.append(f"Function: {other.function.name} -> {self.function.name}")
        if isinstance(self.denominator, ChannelDenominator) and other.denominator != self.denominator:
            result.append(f"Denominator: {other.denominator.name} -> {self.denominator.name}")
        if isinstance(self.event_category, EventCategory) and other.event_category != self.event_category:
            result.append(f"Event Category: {other.event_category.name} -> {self.event_category.name}")
        if isinstance(self.notorious_monster, NotoriousMonster) and other.notorious_monster != self.notorious_monster:
            result.append(f"Notorious Monster: {other.notorious_monster.name} -> {self.notorious_monster.name}")
        if isinstance(self.eureka_instance, EurekaInstance) and other.eureka_instance != self.eureka_instance:
            result.append(f"Eureka Instance: {other.eureka_instance.name} ({other.eureka_instance.value}) -> {self.eureka_instance.name} ({self.eureka_instance.value})")
        if isinstance(self.eureka_instance_name, str) and other.eureka_instance_name != self.eureka_instance_name:
            result.append(f"Eureka Instance Name: {other.eureka_instance_name} -> {self.eureka_instance_name}")
        if not result:
            return "No changes"
        return '\n'.join(result)

    def marshal(self) -> dict:
        return {
            'guild_id': self.marshal_value(self.guild_id),
            'id': self.marshal_value(self.id),
            'channel': {
                'id': self.marshal_value(self.channel_id),
                'name': self._bot.get_text_channel(self.channel_id).name if self.channel_id else 'Unknown'
            },
            'event_type': self.marshal_value(self.event_type),
            'function': self.marshal_value(self.function.name),
            'denominator': self.marshal_value(self.denominator.name),
            'event_category': self.marshal_value(self.event_category.name),
            'notorious_monster': self.marshal_value(self.notorious_monster.name),
            'eureka_instance': self.marshal_value(self.eureka_instance.name),
            'eureka_instance_name': self.marshal_value(self.eureka_instance_name)
        }