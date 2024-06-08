from enum import Enum

class GuildChannelFunction(Enum):
    NONE = 0
    PASSCODES = 1
    SUPPORT_PASSCODES = 2
    LOGGING = 3
    MISSED_POST_CHANNEL = 4
    PL_CHANNEL = 5
    RUN_NOTIFICATION = 6
    EUREKA_TRACKER_NOTIFICATION = 7
    NM_PINGS = 8