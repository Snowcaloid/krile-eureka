from enum import Enum
from typing import List, Optional, Self
from discord.app_commands import Choice

from utils.functions import filter_choices_by_current


class EventCategory(Enum):
    CUSTOM = 'CUSTOM'
    BA = 'BA'
    DRS = 'DRS'
    BOZJA = 'BOZJA'
    CHAOTIC = 'CHAOTIC'

    @classmethod
    def all_category_choices(cls) -> List[Choice]:
        return [
            Choice(name='Custom runs', value=cls.CUSTOM.value + '_CATEGORY'),
            Choice(name='All BA runs', value=cls.BA.value + '_CATEGORY'),
            Choice(name='All DRS runs', value=cls.DRS.value + '_CATEGORY'),
            Choice(name='All Bozja-related runs', value=cls.BOZJA.value + '_CATEGORY'),
            Choice(name='All Chaotic Alliance runs', value=cls.CHAOTIC.value + '_CATEGORY')
        ]

    @classmethod
    def _missing_(cls, value: str) -> Optional[Self]:
        normalized_name = value.replace("_CATEGORY", "")
        return cls.__members__.get(normalized_name, None)

    @classmethod
    def all_category_choices_short(cls) -> List[Choice]:
        return [
            Choice(name='Custom run', value=cls.CUSTOM.value),
            Choice(name='BA', value=cls.BA.value),
            Choice(name='DRS', value=cls.DRS.value),
            Choice(name='Bozja', value=cls.BOZJA.value),
            Choice(name='Chaotic', value=cls.CHAOTIC.value)
        ]

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        return filter_choices_by_current(cls.all_category_choices(), current)

    @classmethod
    def autocomplete_short(cls, current: str) -> List[Choice]:
        return filter_choices_by_current(cls.all_category_choices_short(), current)

    @classmethod
    def is_event_category(cls, event_type: str) -> bool:
        """Check if the given event type is a valid event category."""
        return event_type.replace('_CATEGORY', '') in cls._value2member_map_

    @classmethod
    def event_category_name_to_category(cls, event_category_name: str) -> Self:
        for choice in cls.all_category_choices():
            if choice.name == event_category_name:
                return choice.value
        return cls(event_category_name)