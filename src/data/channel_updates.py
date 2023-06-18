from typing import Dict
from data.runtime_guild_data import RuntimeGuildData
from data.table.channels import InfoTitleType
from threading import Timer

class ChannelUpdates:
    _lock_list: Dict[int, Dict[InfoTitleType, bool]]
    _timer: Timer

    def __init__(self):
        self._lock_list = {}

    def load(self, guild_data: RuntimeGuildData):
        for guild in guild_data._list:
            self._lock_list[guild.guild_id] = {
                InfoTitleType.NEXT_RUN_TYPE: False,
                InfoTitleType.NEXT_RUN_START_TIME: False,
                InfoTitleType.NEXT_RUN_PASSCODE_TIME: False
            }

    def update(self, guild: int, type: InfoTitleType):
        self._lock_list[guild][type] = True
        timer = Timer(600.0, self.allow_update, [guild, type])
        timer.start()

    def can_update(self, guild: int, type: InfoTitleType) -> bool:
        return not self._lock_list[guild][type]

    def allow_update(self, guild: int, type: InfoTitleType):
        self._lock_list[guild][type] = False
