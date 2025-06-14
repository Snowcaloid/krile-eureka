
from enum import Enum
from discord import ButtonStyle
from discord.app_commands import Choice
from typing import Any, Dict, List, Set, Type

from utils.functions import filter_choices_by_current


type GuildID = int


class UNASSIGNED_TYPE:
    name: None
    def __repr__(self) -> str:
        return "<unassigned value>"

    def __bool__(self) -> bool:
        return False


Unassigned = UNASSIGNED_TYPE()


def fix_enum(enum_type: Type[Enum], value: Any):
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


class ChannelDenominator(Enum):
    NONE = ""
    EVENT_TYPE = "event_type"
    EVENT_CATEGORY = "event_category"
    EUREKA_INSTANCE = "eureka_instance"
    NOTORIOUS_MONSTER = "notorious_monster"

    def functions(self) -> List[GuildChannelFunction]:
        """Return a list of GuildChannelFunction that this ChannelDenominator is used for."""
        match self:
            case ChannelDenominator.NONE: return [GuildChannelFunction.NONE]
            case ChannelDenominator.EVENT_TYPE: return [
                GuildChannelFunction.PASSCODES,
                GuildChannelFunction.SUPPORT_PASSCODES,
                GuildChannelFunction.PL_CHANNEL,
                GuildChannelFunction.RUN_NOTIFICATION
            ]
            case ChannelDenominator.EVENT_CATEGORY: return [
                GuildChannelFunction.PASSCODES,
                GuildChannelFunction.SUPPORT_PASSCODES,
                GuildChannelFunction.PL_CHANNEL,
                GuildChannelFunction.RUN_NOTIFICATION
            ]
            case ChannelDenominator.EUREKA_INSTANCE: return [
                GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION
            ]
            case ChannelDenominator.NOTORIOUS_MONSTER: return [
                GuildChannelFunction.NM_PINGS
            ]

    def is_allowed_function(self, function: GuildChannelFunction) -> bool:
        """Check if the function is allowed for this ChannelDenominator."""
        return function in self.functions()


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

class RoleFunction(Enum):
    DEVELOPER = 1
    ADMIN = 2
    RAID_LEADER = 3
    MAIN_PASSCODE_PING = 4
    SUPPORT_PASSCODE_PING = 5
    PL_POST_PING = 6
    RUN_NOTIFICATION = 7
    EUREKA_TRACKER_NOTIFICATION_PING = 8
    NM_PING = 9

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        choices = [
            Choice(name='Raid Leader', value=cls.RAID_LEADER.value),
            Choice(name='Main Passcode Ping', value=cls.MAIN_PASSCODE_PING.value),
            Choice(name='Support Passcode Ping', value=cls.SUPPORT_PASSCODE_PING.value),
            Choice(name='PL Post Ping', value=cls.PL_POST_PING.value),
            Choice(name='Eureka Tracker Notification Ping', value=cls.EUREKA_TRACKER_NOTIFICATION_PING.value),
            Choice(name='Notorious Monster Ping', value=cls.NM_PING.value)
        ]
        return filter_choices_by_current(choices, current)

class RoleDenominator(Enum):
    EVENT_TYPE = "event_type"
    EVENT_CATEGORY = "event_category"
    NOTORIOUS_MONSTER = "notorious_monster"
    EUREKA_INSTANCE = "eureka_instance"

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

class EurekaInstance(Enum):
    ANEMOS = "Anemos"
    PAGOS = "Pagos"
    PYROS = "Pyros"
    HYDATOS = "Hydatos"

    @classmethod
    def choices(cls) -> List[Choice]:
        return [
            Choice(name='Anemos',  value=str(cls.ANEMOS.value)),
            Choice(name='Pagos', value=str(cls.PAGOS.value)),
            Choice(name='Pyros', value=str(cls.PYROS.value)),
            Choice(name='Hydatos', value=str(EurekaInstance.HYDATOS.value))
        ]

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        return filter_choices_by_current(cls.choices(), current)

    def _missing_(self, value: Any) -> str:
        """This method is used to handle cases where the value is not found in the enum."""
        if isinstance(value, int):
            match value:
                case 1: return "Anemos"
                case 2: return "Pagos"
                case 3: return "Pyros"
                case 4: return "Hydatos"
        if isinstance(value, str):
            choice = next((choice for choice in self.choices() if choice.name.lower() == value.lower()), None)
            if choice:
                return choice.value
        return f"Invalid Eureka instance name: {value}"

    @classmethod
    def name_to_value_str(cls, eureka_instance: Any) -> str:
        for intance in cls._value2member_map_:
            if intance.name == eureka_instance.upper():
                return str(intance.value)
        if isinstance(eureka_instance, int):
            return str(eureka_instance)
        return eureka_instance

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

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        nm_choices = NotoriousMonsters.choices()
        if current:
            return filter_choices_by_current(nm_choices, current) + filter_choices_by_current(NotoriousMonsters.alias_choices(), current)
        else:
            return nm_choices

    def _missing_(self, value: Any) -> str:
        """This method is used to handle cases where the value is not found in the enum."""
        if isinstance(value, str):
            choice = next((choice for choice in NotoriousMonsters.choices() if choice.name.lower() == value.lower()), None)
            if choice:
                return choice.value
            choice = next((choice for choice in NotoriousMonsters.alias_choices() if choice.name.lower() == value.lower()), None)
            if choice:
                return choice.value
        return f"Invalid Notorious Monster name: {value}"


class NotoriousMonsters(Dict[NotoriousMonster, str]):
    def __init__(self):
        super().__init__()
        self.aliases = {
            NotoriousMonster.KING_ARTHRO: ['Roi Arthro', 'König Athro', 'Crab'],
            NotoriousMonster.LOUHI: ['Luigi'],
            NotoriousMonster.CASSIE: ['Cassie la copieuse', 'Kopierende Cassie', 'Cassie'],
            NotoriousMonster.PENTHESILEA: ['Penthésilée', 'Penny'],
            NotoriousMonster.GOLDEMAR: ['Roi Goldemar', 'Goldemar'],
            NotoriousMonster.PROVENANCE_WATCHER: ['PW', 'Gardien de Provenance', 'Kristallwächter'],
            NotoriousMonster.LAMEBRIX: ['Wüterix-Söldner'],
            NotoriousMonster.SKOLL: ['Skalli']
        }
        self.update({
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
            NotoriousMonster.SUPPORT: 'Support FATE'
        })

    @classmethod
    def is_nm_type(cls, notorious_monster: str) -> bool:
        return notorious_monster in NOTORIOUS_MONSTERS.values()

    @classmethod
    def name_to_type_str(cls, notorious_monster: Any) -> str:
        for nm_type, nm_name in NOTORIOUS_MONSTERS.items():
            if nm_name == notorious_monster:
                return nm_type.value
        for nm_type, aliases in NOTORIOUS_MONSTERS.aliases.items():
            if notorious_monster in aliases:
                return nm_type.value
        return notorious_monster

    @classmethod
    def choices(cls) -> List[Choice]:
        return [Choice(name=nm_name, value=nm_enum.value) for nm_enum, nm_name in NOTORIOUS_MONSTERS.items()]

    @classmethod
    def alias_choices(cls) -> List[Choice]:
        return [Choice(name=alias, value=nm_enum.value) for nm_enum, aliases in NOTORIOUS_MONSTERS.aliases.items() for alias in aliases]


NOTORIOUS_MONSTERS = NotoriousMonsters()


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