from enum import Enum
import bot
from abc import abstractclassmethod, abstractclassmethod
from discord.app_commands import Choice
from indexedproperty import indexedproperty
from datetime import datetime, timedelta
from time import strftime
from typing import List, Tuple, Type
from nullsafe import _
from data.db.database import pg_timestamp
from data.generators.event_passcode_generator import EventPasscodeGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.tasks.tasks import TaskExecutionType

from utils import DiscordTimestampType, get_discord_member, get_discord_timestamp

PL_FIELDS = ['pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'p61', 'pls']

class EventCategory(Enum):
    CUSTOM = 'CUSTOM'
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
    def type(cl) -> str: 'CUSTOM'
    @abstractclassmethod
    def description(cl) -> str: pass
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
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int) -> str: pass
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
    def schedule_entry_text(cl, rl: str, time: datetime, custom: str) -> str:
        if custom: custom = f' [{custom}]'
        return f'**{strftime("%H:%M", time)} ST ({get_discord_timestamp(time)} LT)**: {cl.short_description()} ({rl}){custom}'

    @classmethod
    def passcode_post_title(cl, time: datetime) -> str:
        return f'{strftime(f"%A, %d-%b-%y %H-%M ST {cl.description()} passcode", time)}'

    @classmethod
    def pl_post_title(cl, time: datetime) -> str:
        return f'{strftime(f"%A, %d-%b-%y %H-%M ST {cl.description()} party leader recruitment", time)}'

    @classmethod
    def dm_title(cl, time: datetime) -> str:
        return f'{strftime(f"%A, %d-%b-%y %H-%M ST {cl.description()} passcode notification", time)}'

    @classmethod
    def as_choice(cl) -> Choice:
        return Choice(name=cl.description(), value=cl.type())

    @classmethod
    def all_types(cl) -> List[str]:
        return [event_base.type() for event_base in Event._registered_events]

    @classmethod
    def by_type(cl, type: str) -> Type['Event']:
        return next((event_base for event_base in cl._registered_events if event_base.type() == type), Event)

class EventCategoryCollection:
    BA_ONLY: List[Event] = Event.all_events_for_category(EventCategory.BA)
    DRS_ONLY: List[Event] = Event.all_events_for_category(EventCategory.DRS)
    BOZJA_ONLY: List[Event] = Event.all_events_for_category(EventCategory.BOZJA)
    CUSTOM_ONLY: List[Event] = [Event]
    BA_WITH_CUSTOM: List[Event] = Event.all_events_for_category(EventCategory.BA) + [Event]
    DRS_WITH_CUSTOM: List[Event] = Event.all_events_for_category(EventCategory.DRS) + [Event]
    BOZJA_WITH_CUSTOM: List[Event] = Event.all_events_for_category(EventCategory.BOZJA) + [Event]
    BA_AND_DRS: List[Event] = Event.all_events_for_category(EventCategory.BA) + Event.all_events_for_category(EventCategory.DRS)
    BA_AND_DRS_WITH_CUSTOM: List[Event] = Event.all_events_for_category(EventCategory.BA) + Event.all_events_for_category(EventCategory.DRS) + [Event]
    DRS_AND_BOZJA: List[Event] = Event.all_events_for_category(EventCategory.DRS) + Event.all_events_for_category(EventCategory.BOZJA)
    DRS_AND_BOZJA_WITH_CUSTOM: List[Event] = Event.all_events_for_category(EventCategory.DRS) + Event.all_events_for_category(EventCategory.BOZJA) + [Event]
    ALL: List[Event] = Event.all_events_for_category(EventCategory.BA) + Event.all_events_for_category(EventCategory.DRS) + Event.all_events_for_category(EventCategory.BOZJA)
    ALL_WITH_CUSTOM: List[Event] = Event.all_events_for_category(EventCategory.BA) + Event.all_events_for_category(EventCategory.DRS) + Event.all_events_for_category(EventCategory.BOZJA) + [Event]

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
                self._raid_leader = record[0]
                self._party_leaders.clear()
                for i in range(1, 7):
                    self._party_leaders.append(record[i])
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
    users: ScheduledEventUserData = ScheduledEventUserData()
    passcode_main: int
    passcode_supp: int
    _description: str

    def load(self, id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = db.query(f'select event_type, pl_post_id, timestamp, description, pass_main, pass_supp from events where id={id}')
            if record:
                for type in Event._registered_events:
                    if type.type() == record[0]:
                        self.base = type
                        break
                self.id = id
                self._pl_post_id = record[1]
                self._time = record[2]
                self._description = record[3]
                self.passcode_main = record[4]
                self.passcode_supp = record[5]
                self.users.load(id)
        finally:
            db.disconnect()

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
        return not self.passcode_main and not self.passcode_supp

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
            passcode_supp=self.passcode_supp)

    @property
    def use_support(self) -> str:
        return self.base.use_support()

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
        return self.base.schedule_entry_text(user.mention, self.time, self.description)

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
        return self.base.pl_button_texts()

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

    def _pl_placeholder(self, pl: str|None) -> str:
        return pl if pl else 'TBD'

    @property
    def pl_post_text(self) -> str:
        guild_data = bot.instance.get_guild(self.guild_id)
        rl = guild_data.get_member(self.users.raid_leader)
        pl1 = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[0])).nick)
        pl2 = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[1])).nick)
        pl3 = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[2])).nick)
        pl4 = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[3])).nick)
        pl5 = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[4])).nick)
        pl6 = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[5])).nick)
        pls = self._pl_placeholder(_(guild_data.get_member(self.users.party_leaders[6])).nick)
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
                bot.instance.data.tasks.add_task(self.time + timedelta(hours=12), TaskExecutionType.REMOVE_OLD_PL_POSTS, {"guild": self.guild_id, "channel": channel_data.id})
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
        channel_data = bot.instance.data.guilds.get(self.guild_id).channels.get(GuildChannelFunction.PL_CHANNEL, self.type)
        if channel_data:
            bot.instance.data.tasks.remove_task_by_data(TaskExecutionType.REMOVE_OLD_PL_POSTS, {"guild": self.guild_id, "channel": channel_data.id})

    async def to_string(self, guild_id: int) -> str:
        # TODO: This object should probably know what guild it belongs to without being told.
        raid_leader = await get_discord_member(guild_id, self.leader)
        discord_timestamp = get_discord_timestamp(self.timestamp, DiscordTimestampType.RELATIVE)
        return f'{self.type} by {raid_leader.display_name} at {self.timestamp} ST {discord_timestamp}'

