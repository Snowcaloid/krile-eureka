from enum import Enum
from typing import List
from discord.app_commands import Choice

class GuildMessageFunction(Enum):
    NONE = 0
    SCHEDULE_POST = 1
    PL_POST = 2
    MISSED_RUN_POST = 3
    MISSED_RUNS_LIST = 4
    WEATHER_POST = 5

    @classmethod
    def all_function_choices(cl) -> List[Choice]:
        return [
            Choice(name='Schedule Posts', value=GuildMessageFunction.SCHEDULE_POST.value),
            Choice(name='Party leader posts', value=GuildMessageFunction.PL_POST.value),
            Choice(name='Missed run posts', value=GuildMessageFunction.MISSED_RUN_POST.value),
            Choice(name='Missed runs lists', value=GuildMessageFunction.MISSED_RUNS_LIST.value),
            Choice(name='Eureka weather posts', value=GuildMessageFunction.WEATHER_POST.value)
        ]