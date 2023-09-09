from enum import Enum

class GuildChannelFunction(Enum):
    NONE = 0
    PASSCODES = 1
    SUPPORT_PASSCODES = 2
    LOGGING = 3
    MISSED_POST_CHANNEL = 4
    PL_CHANNEL = 5