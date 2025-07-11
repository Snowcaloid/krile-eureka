
from enum import Enum
from discord import ButtonStyle
from discord.app_commands import Choice
from typing import Any, Dict, List, Optional, Self

from utils.functions import filter_choices_by_current

# _________ Types ______________________________________________________________________

type GuildID = int


class UNASSIGNED_TYPE:
    name: None
    def __repr__(self) -> str:
        return "<unassigned value>"

    def __bool__(self) -> bool:
        return False


# _________ Enums ______________________________________________________________________

class ChannelFunction(Enum):
    NONE = ''
    PASSCODES = 'passcodes'
    SUPPORT_PASSCODES = 'support_passcodes'
    LOGGING = 'logging'
    RECRUITMENT = 'recruitment'
    EVENT_NOTIFICATION = 'ev_notif'
    EUREKA_TRACKER_NOTIFICATION = 'eureka_tr_notif'
    NM_PINGS = 'nm_pings'


class ChannelDenominator(Enum):
    NONE = ''
    EVENT_TYPE = 'event_type'
    EVENT_CATEGORY = 'event_category'
    EUREKA_INSTANCE = 'eureka_instance'
    NOTORIOUS_MONSTER = 'notorious_monster'

    def functions(self) -> List[ChannelFunction]:
        """Return a list of GuildChannelFunction that this ChannelDenominator is used for."""
        match self:
            case ChannelDenominator.NONE: return [ChannelFunction.NONE]
            case ChannelDenominator.EVENT_TYPE | ChannelDenominator.EVENT_CATEGORY: return [
                ChannelFunction.PASSCODES,
                ChannelFunction.SUPPORT_PASSCODES,
                ChannelFunction.RECRUITMENT,
                ChannelFunction.EVENT_NOTIFICATION
            ]
            case ChannelDenominator.EUREKA_INSTANCE: return [
                ChannelFunction.EUREKA_TRACKER_NOTIFICATION
            ]
            case ChannelDenominator.NOTORIOUS_MONSTER: return [
                ChannelFunction.NM_PINGS
            ]

    def is_allowed_function(self, function: ChannelFunction) -> bool:
        """Check if the function is allowed for this ChannelDenominator."""
        return function in self.functions()


class MessageFunction(Enum):
    NONE = ''
    SCHEDULE = 'schedule'
    EUREKA_INSTANCE_INFO = 'eureka_instance_info'

    @classmethod
    def all_function_choices(cls) -> List[Choice]:
        return [
            Choice(name='Schedule Posts', value=cls.SCHEDULE.value),
            Choice(name='Eureka info', value=cls.EUREKA_INSTANCE_INFO.value)
        ]


class RoleFunction(Enum):
    DEVELOPER = 'dev'
    ADMIN = 'admin'
    RAID_LEADER = 'rl'
    MAIN_PASSCODE_PING = 'pass_ping'
    SUPPORT_PASSCODE_PING = 'supp_pass_ping'
    RECRUITMENT_POST_PING = 'recr_post_ping'
    RUN_NOTIFICATION = 'run_notif'
    EUREKA_TRACKER_NOTIFICATION = 'eureka_tr_notif'
    NOTORIOUS_MONSTER_NOTIFICATION = 'nm_ping'

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        choices = [
            Choice(name='Raid Leader', value=cls.RAID_LEADER.value),
            Choice(name='Main Passcode Ping', value=cls.MAIN_PASSCODE_PING.value),
            Choice(name='Support Passcode Ping', value=cls.SUPPORT_PASSCODE_PING.value),
            Choice(name='PL Post Ping', value=cls.RECRUITMENT_POST_PING.value),
            Choice(name='Run Notification', value=cls.RUN_NOTIFICATION.value),
            Choice(name='Eureka Tracker Notification Ping', value=cls.EUREKA_TRACKER_NOTIFICATION.value),
            Choice(name='Notorious Monster Ping', value=cls.NOTORIOUS_MONSTER_NOTIFICATION.value)
        ]
        return filter_choices_by_current(choices, current)


class RoleDenominator(Enum):
    NONE = ''
    EVENT_TYPE = 'event_type'
    EVENT_CATEGORY = 'event_category'
    NOTORIOUS_MONSTER = 'notorious_monster'
    EUREKA_INSTANCE = 'eureka_instance'

    def functions(self) -> List[RoleFunction]:
        """Return a list of RoleFunction that this RoleDenominator is used for."""
        match self:
            case RoleDenominator.NONE: return [
                RoleFunction.DEVELOPER,
                RoleFunction.ADMIN
            ]
            case RoleDenominator.EVENT_TYPE | RoleDenominator.EVENT_CATEGORY: return [
                RoleFunction.RAID_LEADER,
                RoleFunction.MAIN_PASSCODE_PING,
                RoleFunction.SUPPORT_PASSCODE_PING,
                RoleFunction.RECRUITMENT_POST_PING,
                RoleFunction.RUN_NOTIFICATION
            ]
            case RoleDenominator.EUREKA_INSTANCE: return [
                RoleFunction.EUREKA_TRACKER_NOTIFICATION
            ]
            case RoleDenominator.NOTORIOUS_MONSTER: return [
                RoleFunction.NOTORIOUS_MONSTER_NOTIFICATION
            ]
        return []

    def is_allowed_function(self, function: RoleFunction) -> bool:
        """Check if the function is allowed for this RoleDenominator."""
        return function in self.functions()


class TaskType(Enum):
    NONE = ''
    UPDATE_STATUS = 'update_status'
    SEND_PL_PASSCODES = 'send_pl_passcodes'
    MARK_RUN_AS_FINISHED = 'mark_run_as_finished'
    REMOVE_RECRUITMENT_POST = 'remove_recruitment_post'
    POST_MAIN_PASSCODE = 'post_main_passcode'
    POST_SUPPORT_PASSCODE = 'post_support_passcode'
    UPDATE_EUREKA_INFO_POSTS = 'update_eureka_info_posts'
    RUN_ASYNC_METHOD = 'run_async_method'


class EurekaInstance(Enum):
    ANEMOS = 'Anemos'
    PAGOS = 'Pagos'
    PYROS = 'Pyros'
    HYDATOS = 'Hydatos'

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
                case 1: return 'Anemos'
                case 2: return 'Pagos'
                case 3: return 'Pyros'
                case 4: return 'Hydatos'
        if isinstance(value, str):
            choice = next((choice for choice in self.choices() if choice.name.lower() == value.lower()), None)
            if choice:
                return choice.value
        return f'Invalid Eureka instance name: {value}'

    @classmethod
    def name_to_value_str(cls, eureka_instance: Any) -> str:
        for intance in cls._value2member_map_:
            if intance.name == eureka_instance.upper():
                return str(intance.value)
        if isinstance(eureka_instance, int):
            return str(eureka_instance)
        return eureka_instance


class NotoriousMonster(Enum):
    PAZUZU = 'Pazuzu'
    KING_ARTHRO = 'Crab'
    CASSIE = 'Cassie'
    LOUHI = 'Louhi'
    LAMEBRIX = 'Lame'
    YING_YANG = 'Yy'
    SKOLL = 'Skoll'
    PENTHESILEA = 'Penny'
    MOLECH = 'Molech'
    GOLDEMAR = 'Goldemar'
    CETO = 'Ceto'
    PROVENANCE_WATCHER = 'Pw'
    SUPPORT = 'Support'

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


class EventCategory(Enum):
    CUSTOM = 'custom'
    BA = 'ba'
    FT = 'ft'
    DRS = 'drs'
    BOZJA = 'bozja'
    CHAOTIC = 'chaotic'

    @classmethod
    def all_category_choices(cls) -> List[Choice]:
        return [
            Choice(name='Custom runs', value=cls.CUSTOM.value + '_CATEGORY'),
            Choice(name='All BA runs', value=cls.BA.value + '_CATEGORY'),
            Choice(name='All DRS runs', value=cls.DRS.value + '_CATEGORY'),
            Choice(name='All Bozja-related runs', value=cls.BOZJA.value + '_CATEGORY'),
            Choice(name='All Chaotic Alliance runs', value=cls.CHAOTIC.value + '_CATEGORY')
        ]

    @classmethod
    def _missing_(cls, value: str) -> Optional[Self]:
        normalized_name = value.replace("_CATEGORY", "")
        return cls.__members__.get(normalized_name, None)

    @classmethod
    def all_category_choices_short(cls) -> List[Choice]:
        return [
            Choice(name='Custom run', value=cls.CUSTOM.value),
            Choice(name='BA', value=cls.BA.value),
            Choice(name='DRS', value=cls.DRS.value),
            Choice(name='Bozja', value=cls.BOZJA.value),
            Choice(name='Chaotic', value=cls.CHAOTIC.value)
        ]

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        return filter_choices_by_current(cls.all_category_choices(), current)

    @classmethod
    def autocomplete_short(cls, current: str) -> List[Choice]:
        return filter_choices_by_current(cls.all_category_choices_short(), current)

    @classmethod
    def is_event_category(cls, event_type: str) -> bool:
        """Check if the given event type is a valid event category."""
        return event_type.replace('_CATEGORY', '') in cls._value2member_map_

    @classmethod
    def event_category_name_to_category(cls, event_category_name: str) -> Self:
        for choice in cls.all_category_choices():
            if choice.name == event_category_name:
                return choice.value
        return cls(event_category_name)


class ButtonType(Enum):
    POSITION_PICK_BUTTON = 'position_pick_button'
    ROLE_SELECTION = 'role_selection'
    ROLE_DISPLAY = 'role_display'
    RECRUITMENT = 'recruitment'
    ASSIGN_TRACKER = 'assign_tracker'
    GENERATE_TRACKER = 'generate_tracker'
    SEND_PL_GUIDE = 'send_pl_guide'

# _________ Constants __________________________________________________________________

Unassigned = UNASSIGNED_TYPE()

NOTORIOUS_MONSTERS = NotoriousMonsters()

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
