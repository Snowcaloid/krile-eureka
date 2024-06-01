from enum import Enum

from discord import Member
import bot
from abc import abstractclassmethod, abstractclassmethod
from discord.app_commands import Choice
from indexedproperty import indexedproperty
from datetime import datetime, timedelta
from typing import List, Tuple, Type
from data.db.database import pg_timestamp
from data.generators.event_passcode_generator import EventPasscodeGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.tasks.tasks import TaskExecutionType

from utils import DiscordTimestampType, get_discord_member, get_discord_timestamp

PL_FIELDS = ['pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'pl6', 'pls']

class EventCategory(Enum):
    CUSTOM = 'CUSTOM_CATEGORY'
    BA = 'BA_CATEGORY'
    DRS = 'DRS_CATEGORY'
    BOZJA = 'BOZJA_CATEGORY'

    @classmethod
    def all_category_choices(cl) -> List[Choice]:
        return [
            Choice(name='Custom runs', value=cl.CUSTOM.value),
            Choice(name='All BA runs', value=cl.BA.value),
            Choice(name='All DRS runs', value=cl.DRS.value),
            Choice(name='All Bozja-related runs', value=cl.BOZJA.value)
        ]

    @classmethod
    def all_category_choices_short(cl) -> List[Choice]:
        return [
            Choice(name='Custom run', value=cl.CUSTOM.value),
            Choice(name='BA', value=cl.BA.value),
            Choice(name='DRS', value=cl.DRS.value),
            Choice(name='Bozja', value=cl.BOZJA.value)
        ]

    @classmethod
    def as_choice(cl, category: Type['EventCategory']) -> Choice:
        return next(choice for choice in cl.all_category_choices() if choice.value == category.value)

    @classmethod
    def calculate_choices(cl, use_ba: bool, use_drs: bool, use_bozja: bool, use_custom: bool) -> List[Choice]:
        result: List[Event] = []
        if use_ba: result = result + cl.as_choice(EventCategory.BA)
        if use_drs: result = result + cl.as_choice(EventCategory.DRS)
        if use_bozja: result = result + cl.as_choice(EventCategory.BOZJA)
        if use_custom: result = result + cl.as_choice(EventCategory.CUSTOM)
        return result

class Event:
    _registered_events: List[Type['Event']] = []

    @classmethod
    def register(cl):
        Event._registered_events.append(cl)

    @classmethod
    def all_events_for_category(cl, category: EventCategory) -> List[Type['Event']]:
        return [event_base for event_base in Event._registered_events if event_base.category() == category]

    @classmethod
    def all_choices_for_category(cl, category: EventCategory) -> List[Choice]:
        return [event_base.as_choice() for event_base in Event.all_events_for_category(category)]

    @classmethod
    def type(cl) -> str: return 'CUSTOM'
    @classmethod
    def description(cl) -> str: return 'Custom run'
    @abstractclassmethod
    def short_description(cl) -> str: pass
    @classmethod
    def category(cl) -> EventCategory: return EventCategory.CUSTOM
    @classmethod
    def use_pl_posts(cl) -> bool: return False
    @classmethod
    def use_passcodes(cl) -> bool: return False
    @classmethod
    def use_pl_post_thread(cl) -> bool: return False
    @classmethod
    def delete_pl_posts(cl) -> bool: return True
    @abstractclassmethod
    def use_support(cl) -> bool: pass
    @abstractclassmethod
    def main_passcode_text(cl, rl: str, passcode: int) -> str: pass
    @abstractclassmethod
    def support_passcode_text(cl, rl: str, passcode: int) -> str: pass
    @abstractclassmethod
    def pl_post_text(cl, rl: str, pl1: str, pl2: str, pl3: str,
                     pl4: str, pl5: str, pl6: str, pls: str) -> str: pass
    @abstractclassmethod
    def party_leader_dm_text(cl, party: str, passcode: int) -> str: pass
    @abstractclassmethod
    def support_party_leader_dm_text(cl, passcode: int) -> str: pass
    @abstractclassmethod
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int, use_support: bool) -> str: pass
    @abstractclassmethod
    def pl_passcode_delay(cl) -> timedelta: pass
    @abstractclassmethod
    def support_passcode_delay(cl) -> timedelta: pass
    @abstractclassmethod
    def main_passcode_delay(cl) -> timedelta: pass
    @abstractclassmethod
    def pl_post_thread_title(cl, time: datetime) -> str: pass
    @abstractclassmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]: pass

    @classmethod
    def schedule_entry_text(cl, rl: str, time: datetime, custom: str, use_support: bool) -> str:
        if custom: custom = f' [{custom}]'
        support_text = ' (__No support__)' if cl.use_support() and not use_support else ''
        server_time = time.strftime('%H:%M')
        return f'**{server_time} ST ({get_discord_timestamp(time)} LT)**: {cl.short_description()} ({rl}){support_text}{custom}'

    @classmethod
    def passcode_post_title(cl, time: datetime) -> str:
        return f'{time.strftime(f"%A, %d-%b-%y %H:%M ST")} ({get_discord_timestamp(time)} LT) {cl.description()} passcode'

    @classmethod
    def pl_post_title(cl, time: datetime) -> str:
        return f'{time.strftime(f"%A, %d-%b-%y %H:%M ST")} ({get_discord_timestamp(time)} LT) {cl.description()} party leader recruitment'

    @classmethod
    def dm_title(cl, time: datetime) -> str:
        return f'{time.strftime(f"%A, %d-%b-%y %H:%M ST")} ({get_discord_timestamp(time)} LT) {cl.description()} passcode notification'

    @classmethod
    def as_choice(cl) -> Choice:
        return Choice(name=cl.description(), value=cl.type())

    @classmethod
    def all_types(cl) -> List[str]:
        return [event_base.type() for event_base in Event._registered_events]

    @classmethod
    def by_type(cl, type: str) -> Type['Event']:
        return next((event_base for event_base in Event._registered_events if event_base.type() == type), Event)

class EventCategoryCollection:
    ALL_WITH_CUSTOM: List[Event]

    @classmethod
    def calculate_choices(cl, use_ba: bool, use_drs: bool, use_bozja: bool, use_custom: bool) -> List[Choice]:
        result: List[Event] = []
        if use_ba: result = result + Event.all_events_for_category(EventCategory.BA)
        if use_drs: result = result + Event.all_events_for_category(EventCategory.DRS)
        if use_bozja: result = result + Event.all_events_for_category(EventCategory.BOZJA)
        if use_custom: result = result + [Event]
        return [event_base.as_choice() for event_base in result]

class ScheduledEventUserData:
    event_id: int
    _raid_leader: int
    _party_leaders: List[int]

    def load(self, event_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.event_id = event_id
            record = db.query(f'select raid_leader, pl1, pl2, pl3, pl4, pl5, pl6, pls from events where id={event_id}')
            if record:
                self._raid_leader = record[0][0]
                self._party_leaders = []
                for i in range(1, 8):
                    self._party_leaders.append(record[0][i])
        finally:
            db.disconnect()

    @property
    def raid_leader(self) -> int:
        return self._raid_leader

    @raid_leader.setter
    def raid_leader(self, value: int) -> None:
        if value == self.raid_leader: return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set raid_leader={value} where id={self.event_id}')
            self.load(self.event_id)
        finally:
            db.disconnect()

    @indexedproperty
    def party_leaders(self, index: int) -> int:
        return self._party_leaders[index]

    @party_leaders.setter
    def party_leaders(self, index: int, value: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            bot.instance.data.db.query(f'update events set {PL_FIELDS[index]}={value} where id={self.event_id}')
            self.load(self.event_id)
        finally:
            db.disconnect()

class ScheduledEvent:
    base: Type[Event]
    id: int
    _pl_post_id: int
    _time: datetime
    guild_id: int
    users: ScheduledEventUserData
    passcode_main: int
    passcode_supp: int
    _description: str
    _use_support: bool

    def __init__(self):
        self.users = ScheduledEventUserData()

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select event_type, pl_post_id, timestamp, description, pass_main, pass_supp, guild_id, use_support from events where id={id}')
            if record:
                for type in Event._registered_events:
                    if type.type() == record[0][0]:
                        self.base = type
                        break
                self.id = id
                self._pl_post_id = record[0][1]
                self._time = record[0][2]
                self._description = record[0][3]
                self.passcode_main = record[0][4]
                self.passcode_supp = record[0][5]
                self.guild_id = record[0][6]
                self._use_support = type.use_support() and record[0][7]
                self.users.load(id)
        finally:
            db.disconnect()

    @property
    def real_description(self) -> str:
        return self._description

    @property
    def description(self) -> str:
        if self.base.category == EventCategory.CUSTOM:
            return self._description
        else:
            return self.base.description()

    @description.setter
    def description(self, value: str) -> None:
        if value == self._description: return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set description=\'{value}\' where id={self.id}')
            self.load(self.id)
        finally:
            db.disconnect()

    @property
    def short_description(self) -> str:
        return self.base.short_description()

    @property
    def time(self) -> datetime:
        return self._time

    @time.setter
    def time(self, value: datetime) -> None:
        if value == self.auto_passcode: return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set timestamp={pg_timestamp(value)} where id={self.id}')
            self.load(self.id)
        finally:
            db.disconnect()

    @property
    def auto_passcode(self) -> bool:
        return self.passcode_main != 0 and self.passcode_supp != 0

    @auto_passcode.setter
    def auto_passcode(self, value: bool) -> None:
        if value == self.auto_passcode: return
        db = bot.instance.data.db
        db.connect()
        try:
            if value:
                db.query(f'update events set pass_main={str(EventPasscodeGenerator.generate())}, pass_supp={str(EventPasscodeGenerator.generate())} where id={self.id}')
            else:
                db.query(f'update events set pass_main=0, pass_supp=0 where id={self.id}')
            self.load(self.id)
        finally:
            db.disconnect()

    @property
    def dm_title(self) -> str:
        return self.base.dm_title(time=self.time)

    @property
    def raid_leader_dm_text(self) -> str:
        return self.base.raid_leader_dm_text(
            passcode_main=self.passcode_main,
            passcode_supp=self.passcode_supp,
            use_support=self.use_support)

    @property
    def use_support(self) -> bool:
        return self._use_support

    @use_support.setter
    def use_support(self, value: bool) -> None:
        if (value == self._use_support) or not self.base.use_support(): return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set use_support={value} where id={self.id}')
            self.load(self.id)
        finally:
            db.disconnect()

    @property
    def use_pl_posts(self) -> str:
        return self.base.use_pl_posts()

    @property
    def delete_pl_posts(self) -> str:
        return self.base.delete_pl_posts()

    @property
    def support_party_leader_dm_text(self) -> str:
        return self.base.support_party_leader_dm_text(passcode=self.passcode_supp)

    @property
    def schedule_entry_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.base.schedule_entry_text(user.mention, self.time, self.real_description, self._use_support)

    @property
    def category(self) -> EventCategory:
        return self.base.category()

    @property
    def type(self) -> str:
        return self.base.type()

    @type.setter
    def type(self, value: str):
        if value == self.type: return
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set event_type=\'{value}\' where id={self.id}')
            self.load(self.id)
        finally:
            db.disconnect()

    @property
    def use_pl_post_thread(self) -> str:
        return self.base.use_pl_post_thread()

    @property
    def pl_post_thread_title(self) -> str:
        return self.base.pl_post_thread_title(self.time)

    @property
    def main_passcode_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.base.main_passcode_text(user.mention, self.passcode_main)

    @property
    def support_passcode_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.base.support_passcode_text(user.mention, self.passcode_supp)

    @property
    def passcode_post_title(self) -> str:
        return self.base.passcode_post_title(self.time)

    @property
    def pl_button_texts(self) -> Tuple[str, str, str, str, str, str, str]:
        result = self.base.pl_button_texts()
        if not self.use_support:
            result_list = list(result)
            result_list[6] = ''
            result = tuple(result_list)
        return result

    @property
    def pl_post_title(self) -> str:
        return self.base.pl_post_title(self.time)

    @property
    def pl_passcode_delay(self) -> timedelta:
        return self.base.pl_passcode_delay()

    @property
    def main_passcode_delay(self) -> timedelta:
        return self.base.main_passcode_delay()

    @property
    def support_passcode_delay(self) -> timedelta:
        return self.base.support_passcode_delay()

    def _pl_placeholder(self, member: Member) -> str:
        return member.display_name if member else 'TBD'

    @property
    def pl_post_text(self) -> str:
        guild = bot.instance.get_guild(self.guild_id)
        rl = guild.get_member(self.users.raid_leader)
        pl1 = self._pl_placeholder(guild.get_member(self.users.party_leaders[0]))
        pl2 = self._pl_placeholder(guild.get_member(self.users.party_leaders[1]))
        pl3 = self._pl_placeholder(guild.get_member(self.users.party_leaders[2]))
        pl4 = self._pl_placeholder(guild.get_member(self.users.party_leaders[3]))
        pl5 = self._pl_placeholder(guild.get_member(self.users.party_leaders[4]))
        pl6 = self._pl_placeholder(guild.get_member(self.users.party_leaders[5]))
        pls = self._pl_placeholder(guild.get_member(self.users.party_leaders[6])) if self.use_support else None

        return self.base.pl_post_text(rl.mention, pl1, pl2, pl3, pl4, pl5, pl6, pls)

    def party_leader_dm_text(self, index: int) -> str:
        return self.base.party_leader_dm_text(
            party=self.pl_button_texts[index],
            passcode=self.passcode_main)

    @property
    def pl_post_id(self) -> int:
        return self._pl_post_id

    @pl_post_id.setter
    def pl_post_id(self, value: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set pl_post_id={value} where id={self.id}')
            self.load(self.id)
        finally:
            db.disconnect()

    def create_tasks(self) -> None:
        bot.instance.data.tasks.add_task(self.time, TaskExecutionType.REMOVE_OLD_RUNS, {"id": self.id})
        if self.use_pl_posts and self.delete_pl_posts:
            channel_data = bot.instance.data.guilds.get(self.guild_id).channels.get(GuildChannelFunction.PL_CHANNEL, self.type)
            if channel_data:
                bot.instance.data.tasks.add_task(self.time + timedelta(hours=12), TaskExecutionType.REMOVE_OLD_MESSAGE, {"guild": self.guild_id, "message_id": self.pl_post_id})
        if not self.auto_passcode: return
        bot.instance.data.tasks.add_task(self.time - self.main_passcode_delay, TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        bot.instance.data.tasks.add_task(self.time - self.pl_passcode_delay, TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild_id, "entry_id": self.id})
        if self.use_support:
            bot.instance.data.tasks.add_task(self.time - self.support_passcode_delay, TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})

    def delete_tasks(self) -> None:
        bot.instance.data.tasks.remove_task_by_data(TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild_id, "entry_id": self.id})
        bot.instance.data.tasks.remove_task_by_data(TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        bot.instance.data.tasks.remove_task_by_data(TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        bot.instance.data.tasks.remove_task_by_data(TaskExecutionType.REMOVE_OLD_RUNS, {"id": self.id})
        bot.instance.data.tasks.remove_task_by_data(TaskExecutionType.REMOVE_OLD_MESSAGE, {"guild": self.guild_id, "message_id": self.pl_post_id})

    def recreate_tasks(self) -> None:
        self.delete_tasks()
        self.create_tasks()

    async def to_string(self) -> str:
        raid_leader = await get_discord_member(self.guild_id, self.users.raid_leader)
        discord_timestamp = get_discord_timestamp(self.time, DiscordTimestampType.RELATIVE)
        return f'{self.type} by {raid_leader.display_name} at {self.time} ST {discord_timestamp}'


