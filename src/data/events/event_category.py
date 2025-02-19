from enum import Enum
from typing import List
from discord.app_commands import Choice


class EventCategory(Enum):
    CUSTOM = 'CUSTOM'
    BA = 'BA'
    DRS = 'DRS'
    BOZJA = 'BOZJA'
    CHAOTIC = 'CHAOTIC'

    @classmethod
    def all_category_choices(cl) -> List[Choice]:
        return [
            Choice(name='Custom runs', value=cl.CUSTOM.value + '_CATEGORY'),
            Choice(name='All BA runs', value=cl.BA.value + '_CATEGORY'),
            Choice(name='All DRS runs', value=cl.DRS.value + '_CATEGORY'),
            Choice(name='All Bozja-related runs', value=cl.BOZJA.value + '_CATEGORY'),
            Choice(name='All Chaotic Alliance runs', value=cl.CHAOTIC.value + '_CATEGORY')
        ]

    @classmethod
    def _missing_(cls, value):
        normalized_name = value.replace("_CATEGORY", "")
        return cls.__members__.get(normalized_name, None)

    @classmethod
    def all_category_choices_short(cl) -> List[Choice]:
        return [
            Choice(name='Custom run', value=cl.CUSTOM.value),
            Choice(name='BA', value=cl.BA.value),
            Choice(name='DRS', value=cl.DRS.value),
            Choice(name='Bozja', value=cl.BOZJA.value),
            Choice(name='Chaotic', value=cl.CHAOTIC.value)
        ]