
from enum import Enum
from discord import ButtonStyle
from discord.app_commands import Choice
from typing import Dict, List, Type

from utils.functions import filter_by_current


type GuildID = int

class _Unassigned:
    def __repr__(self) -> str:
        return "<unassigned value>"

Unassigned = _Unassigned()

def fix_enum(enum_type: Type[Enum], value: any):
    if isinstance(value, enum_type):
        return value
    else:
        return enum_type(value) if value is not None and value is not Unassigned else None

class GuildChannelFunction(Enum):
    NONE = 0
    PASSCODES = 1
    SUPPORT_PASSCODES = 2
    LOGGING = 3
    PL_CHANNEL = 5
    RUN_NOTIFICATION = 6
    EUREKA_TRACKER_NOTIFICATION = 7
    NM_PINGS = 8


class GuildMessageFunction(Enum):
    NONE = 0
    SCHEDULE_POST = 1
    PL_POST = 2
    WEATHER_POST = 5
    EUREKA_INFO = 6

    @classmethod
    def all_function_choices(cls) -> List[Choice]:
        return [
            Choice(name='Schedule Posts', value=cls.SCHEDULE_POST.value),
            Choice(name='Party leader posts', value=cls.PL_POST.value),
            Choice(name='Eureka weather posts', value=cls.WEATHER_POST.value),
            Choice(name='Eureka info', value=cls.EUREKA_INFO.value)
        ]

class GuildRoleFunction(Enum):
    DEVELOPER = 1
    ADMIN = 2
    RAID_LEADER = 3
    MAIN_PASSCODE_PING = 4
    SUPPORT_PASSCODE_PING = 5
    PL_POST_PING = 6
    EVENT_NOTIFICATION_PING = 7
    RUN_NOTIFICATION = 8
    EUREKA_TRACKER_NOTIFICATION_PING = 9
    NM_PING = 10
    
    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        choices = [
            Choice(name='Raid Leader', value=cls.RAID_LEADER.value),
            Choice(name='Main Passcode Ping', value=cls.MAIN_PASSCODE_PING.value),
            Choice(name='Support Passcode Ping', value=cls.SUPPORT_PASSCODE_PING.value),
            Choice(name='PL Post Ping', value=cls.PL_POST_PING.value),
            Choice(name='Event Notification Ping', value=cls.EVENT_NOTIFICATION_PING.value),
            Choice(name='Eureka Tracker Notification Ping', value=cls.EUREKA_TRACKER_NOTIFICATION_PING.value),
            Choice(name='Notorious Monster Ping', value=cls.NM_PING.value)
        ]
        return filter_by_current(choices, current)

class TaskExecutionType(Enum):
    NONE = 0
    UPDATE_STATUS = 1
    SEND_PL_PASSCODES = 2
    MARK_RUN_AS_FINISHED = 3
    REMOVE_RECRUITMENT_POST = 4
    POST_MAIN_PASSCODE = 5
    POST_SUPPORT_PASSCODE = 6
    UPDATE_EUREKA_INFO_POSTS = 9
    RUN_ASYNC_METHOD = 10

class EurekaTrackerZone(Enum):
    ANEMOS = 1
    PAGOS = 2
    PYROS = 3
    HYDATOS = 4

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        return filter_by_current([
            Choice(name='Anemos',  value=str(cls.ANEMOS.value)),
            Choice(name='Pagos', value=str(cls.PAGOS.value)),
            Choice(name='Pyros', value=str(cls.PYROS.value)),
            Choice(name='Hydatos', value=str(EurekaTrackerZone.HYDATOS.value))
        ], current)

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
    
    @staticmethod
    def _alterantive_nm_names(nm_choices: List[Choice], current: str) -> List[Choice]:
        choices: List[Choice] = []
        for choice in nm_choices:
            aliases = NM_ALIASES.get(NotoriousMonster(choice.value), None)
            if aliases:
                for alias in aliases:
                    if alias.lower().startswith(current.lower()):
                        choices.append(Choice(name=alias, value=choice.value))
        return choices
    
    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        nm_choices = [Choice(name=nm_name, value=nm_enum.value) for nm_enum, nm_name in NOTORIOUS_MONSTERS.items()]
        if current:
            return filter_by_current(nm_choices, current) + cls._alterantive_nm_names(nm_choices, current)
        else:
            return nm_choices

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