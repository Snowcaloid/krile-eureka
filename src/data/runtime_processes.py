from abc import abstractmethod
from enum import Enum
from typing import List

class RunTimeProcessType(Enum):
    NONE = 0
    EMBED_CREATION = 1

class RunningProcessRecord:
    user: int
    type: RunTimeProcessType

    def __init__(self, user: int, type: RunTimeProcessType) -> None:
        self.user = user
        self.type = type

class ProcessListener:
    @abstractmethod
    def on_finish_process(self, user: int, type: RunTimeProcessType) -> None: pass

class RunTimeProccesses:
    """Runtime data object for the user's queries.
    This object has no equivalent database entity.
    """
    _list: List[RunningProcessRecord] = []
    _owner: ProcessListener

    def __init__(self, owner: ProcessListener):
        self._owner = owner

    def start(self, user: int, type: RunTimeProcessType) -> bool:
        if user in self._list:
            return False
        else:
            self._list.append(RunningProcessRecord(user, type))
        return True

    def running(self, user: int, type: RunTimeProcessType) -> bool:
        for data in self._list:
            if data.user == user and data.type == type:
                return True

        return False

    def stop(self, user: int, type: RunTimeProcessType) -> bool:
        if self.running(user, type):
            for data in self._list:
                if data.user == user and data.type == type:
                    self._list.remove(data)

            self._owner.on_finish_process(user, type)
        else:
            return False
        return True
