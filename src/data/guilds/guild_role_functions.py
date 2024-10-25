
from enum import Enum
from typing import List
from discord.app_commands import Choice

class GuildRoleFunction(Enum):
    NONE = 0
    ALLOW_MISSED_RUN_APPLICATION = 1
    FORBID_MISSED_RUN_APPLICATION = 2
    RAID_LEADER = 3

    @classmethod
    def all_function_choices(cl) -> List[Choice]:
        return [
            Choice(name='Allow missed run applications', value=GuildRoleFunction.ALLOW_MISSED_RUN_APPLICATION.value),
            Choice(name='Forbid missed run applications', value=GuildRoleFunction.FORBID_MISSED_RUN_APPLICATION.value),
            Choice(name='Raid Leader', value=GuildRoleFunction.RAID_LEADER.value)
        ]