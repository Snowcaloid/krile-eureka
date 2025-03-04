
from enum import Enum
from discord import ButtonStyle
from discord.app_commands import Choice
from typing import Dict, List


type GuildID = int

class GuildChannelFunction(Enum):
    NONE = 0
    PASSCODES = 1
    SUPPORT_PASSCODES = 2
    LOGGING = 3
    PL_CHANNEL = 5
    RUN_NOTIFICATION = 6
    EUREKA_TRACKER_NOTIFICATION = 7
    NM_PINGS = 8

class GuildPingType(Enum):
    NONE = 0
    MAIN_PASSCODE = 1
    SUPPORT_PASSCODE = 2
    PL_POST = 3
    RUN_NOTIFICATION = 4
    EUREKA_TRACKER_NOTIFICATION = 5
    NM_PING = 6

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

class GuildRoleFunction(Enum):
    NONE = 0
    DEVELOPER = 1
    ADMIN = 2
    RAID_LEADER = 3

    @classmethod
    def all_function_choices(cl) -> List[Choice]:
        return [
            Choice(name='', value=GuildRoleFunction.DEVELOPER.value),
            Choice(name='Admin', value=GuildRoleFunction.ADMIN.value),
            Choice(name='Raid Leader', value=GuildRoleFunction.RAID_LEADER.value)
        ]

class TaskExecutionType(Enum):
    NONE = 0
    UPDATE_STATUS = 1
    SEND_PL_PASSCODES = 2
    REMOVE_OLD_RUNS = 3
    REMOVE_OLD_MESSAGE = 4
    POST_MAIN_PASSCODE = 5
    POST_SUPPORT_PASSCODE = 6
    REMOVE_BUTTONS = 8
    UPDATE_EUREKA_INFO_POSTS = 9

class EurekaTrackerZone(Enum):
    ANEMOS = 1
    PAGOS = 2
    PYROS = 3
    HYDATOS = 4

class NotoriousMonster(Enum):
    PAZUZU = 'PAZUZU'
    KING_ARTHRO = 'CRAB'
    CASSIE = 'CASSIE'
    LOUHI = 'LOUHI'
    LAMEBRIX = 'LAME'
    YING_YANG = 'YY'
    SKOLL = 'SKOLL'
    PENTHESILEA = 'PENNY'
    MOLECH = 'MOLECH'
    GOLDEMAR = 'GOLDEMAR'
    CETO = 'CETO'
    PROVENANCE_WATCHER = 'PW'
    SUPPORT = 'SUPPORT'

NOTORIOUS_MONSTERS: Dict[NotoriousMonster, str] = {
    NotoriousMonster.PAZUZU: 'Pazuzu',
    NotoriousMonster.KING_ARTHRO: 'King Arthro',
    NotoriousMonster.CASSIE: 'Copycat Cassie',
    NotoriousMonster.LOUHI: 'Louhi',
    NotoriousMonster.LAMEBRIX: 'Lamebrix Strikebocks',
    NotoriousMonster.YING_YANG: 'Ying-Yang',
    NotoriousMonster.SKOLL: 'Skoll',
    NotoriousMonster.PENTHESILEA: 'Penthesilea',
    NotoriousMonster.MOLECH: 'Molech',
    NotoriousMonster.GOLDEMAR: 'King Goldemar',
    NotoriousMonster.CETO: 'Ceto',
    NotoriousMonster.PROVENANCE_WATCHER: 'Provenance Watcher',
    NotoriousMonster.SUPPORT: 'Support FATE',
}

NM_ALIASES: Dict[NotoriousMonster, List[str]] = {
    NotoriousMonster.KING_ARTHRO: ['Roi Arthro', 'König Athro', 'Crab'],
    NotoriousMonster.LOUHI: ['Luigi'],
    NotoriousMonster.CASSIE: ['Cassie la copieuse', 'Kopierende Cassie', 'Cassie'],
    NotoriousMonster.PENTHESILEA: ['Penthésilée', 'Penny'],
    NotoriousMonster.GOLDEMAR: ['Roi Goldemar', 'Goldemar'],
    NotoriousMonster.PROVENANCE_WATCHER: ['PW', 'Gardien de Provenance', 'Kristallwächter'],
    NotoriousMonster.LAMEBRIX: ['Wüterix-Söldner'],
    NotoriousMonster.SKOLL: ['Skalli']
}


class ButtonType(Enum):
    PICK_BUTTON = 0
    ROLE_SELECTION = 1
    ROLE_DISPLAY = 2
    PL_POST = 3
    ASSIGN_TRACKER = 5
    GENERATE_TRACKER = 6
    SEND_PL_GUIDE = 7


BUTTON_STYLE_DESCRIPTIONS: Dict[ButtonStyle, str] = {
    ButtonStyle.primary: 'Blue',
    ButtonStyle.secondary: 'Grey',
    ButtonStyle.success: 'Green',
    ButtonStyle.danger: 'Red',
    ButtonStyle.link: 'Blue Link'
}
BUTTON_TYPE_DESCRIPTIONS: Dict[ButtonType, str] = {
    ButtonType.ROLE_SELECTION: 'Role',
    ButtonType.ROLE_DISPLAY: 'Role display'
}
BUTTON_TYPE_CHOICES: Dict[str, ButtonType] = {
    'role': ButtonType.ROLE_SELECTION,
    'r': ButtonType.ROLE_SELECTION,
    'roledisp': ButtonType.ROLE_DISPLAY,
    'rd': ButtonType.ROLE_DISPLAY,
}
BUTTON_STYLE_CHOICES: Dict[str, ButtonStyle] = {
    'grey': ButtonStyle.secondary,
    'gray': ButtonStyle.secondary,
    'blue': ButtonStyle.primary,
    'green': ButtonStyle.success,
    'red': ButtonStyle.danger,
    'link': ButtonStyle.link
}