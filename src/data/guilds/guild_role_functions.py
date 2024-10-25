
from enum import Enum
from typing import List
from discord.app_commands import Choice

class GuildRoleFunction(Enum):
    NONE = 0
    RAID_LEADER = 3

    @classmethod
    def all_function_choices(cl) -> List[Choice]:
        return [
            Choice(name='Raid Leader', value=GuildRoleFunction.RAID_LEADER.value)
        ]