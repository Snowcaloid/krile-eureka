from enum import Enum
from typing import List
from discord.app_commands import Choice

class GuildMessageFunction(Enum):
    NONE = 0
    SCHEDULE_POST = 1
    PL_POST = 2
    WEATHER_POST = 5
    EUREKA_INFO = 6

    @classmethod
    def all_function_choices(cl) -> List[Choice]:
        return [
            Choice(name='Schedule Posts', value=GuildMessageFunction.SCHEDULE_POST.value),
            Choice(name='Party leader posts', value=GuildMessageFunction.PL_POST.value),
            Choice(name='Eureka weather posts', value=GuildMessageFunction.WEATHER_POST.value),
            Choice(name='Eureka info', value=GuildMessageFunction.EUREKA_INFO.value)
        ]