from enum import Enum

from discord import Interaction, Member
import bot
from abc import abstractclassmethod
from discord.app_commands import Choice
from indexedproperty import indexedproperty
from datetime import datetime, timedelta
from typing import List, Tuple, Type
from data.db.sql import SQL, Record
from data.events.signup import Signup
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
    @classmethod
    def dm_text(cl, party: str, passcode: int) -> str: return (
        'Please open Adventuring Forays Tab in the Private Party Finder section and join the party with the passcode provided.\n\n'
        f'Your party is **party {party}**.\n'
        f'The passcode is **{str(passcode).zfill(4)}**.\n\n'
        'Please make sure to be prepared for the run.\n'
        'If you have any questions, please ask the raid leader or party leader.\n'
        '**Make sure that you enter the party before the run starts.**'
    )
    @abstractclassmethod
    def support_party_leader_dm_text(cl, passcode: int) -> str: pass
    @abstractclassmethod
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int, use_support: bool) -> str: pass
    @abstractclassmethod
    def pl_passcode_delay(cl) -> timedelta: return timedelta()
    @abstractclassmethod
    def support_passcode_delay(cl) -> timedelta: return timedelta()
    @abstractclassmethod
    def main_passcode_delay(cl) -> timedelta: return timedelta()
    @abstractclassmethod
    def pl_post_thread_title(cl, time: datetime) -> str: pass
    @abstractclassmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]: pass

    @classmethod
    def schedule_entry_text(cl, rl: str, time: datetime, custom: str, use_support: bool) -> str:
        support_text = ' (__No support__)' if cl.use_support() and not use_support else ''
        server_time = time.strftime('%H:%M')
        if cl.short_description() is None:
            return f'**{server_time} ST ({get_discord_timestamp(time)} LT)**: {custom} ({rl}){support_text}'
        else:
            if custom: custom = f' [{custom}]'
            return f'**{server_time} ST ({get_discord_timestamp(time)} LT)**: {cl.short_description()} ({rl}){support_text}{custom}'

    @classmethod
    def passcode_post_title(cl, time: datetime) -> str:
        return f'{time.strftime(f"%A, %d-%b-%y %H:%M ST")} ({get_discord_timestamp(time)} LT) {cl.description()} Passcode'

    @classmethod
    def pl_post_title(cl, time: datetime) -> str:
        return f'{time.strftime(f"%A, %d-%b-%y %H:%M ST")} ({get_discord_timestamp(time)} LT) {cl.description()} Party Leader Recruitment'

    @classmethod
    def dm_title(cl, time: datetime) -> str:
        return f'{time.strftime(f"%A, %d-%b-%y %H:%M ST")} ({get_discord_timestamp(time)} LT) {cl.description()} Passcode Notification'

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
        self.event_id = event_id
        record = SQL('events').select(fields=['raid_leader', 'pl1', 'pl2', 'pl3',
                                              'pl4', 'pl5', 'pl6', 'pls'],
                                      where=f'id={event_id}')
        if record:
            self._raid_leader = record['raid_leader']
            self._party_leaders = [
                record['pl1'], record['pl2'], record['pl3'], record['pl4'], record['pl5'], record['pl6'], record['pls']
            ]

    @property
    def raid_leader(self) -> int:
        return self._raid_leader

    @raid_leader.setter
    def raid_leader(self, value: int) -> None:
        if value == self.raid_leader: return
        SQL('events').update(Record(raid_leader=value), f'id={self.event_id}')
        self.load(self.event_id)

    @indexedproperty
    def party_leaders(self, index: int) -> int:
        return self._party_leaders[index]

    @party_leaders.setter
    def party_leaders(self, index: int, value: int) -> None:
        record = Record()
        record[PL_FIELDS[index]] = value
        SQL('events').update(record, f'id={self.event_id}')
        self.load(self.event_id)

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
    signup: Signup

    def __init__(self):
        self.users = ScheduledEventUserData()
        self.signup = Signup()

    def load(self, id: int) -> None:
        record = SQL('events').select(fields=['event_type', 'pl_post_id', 'timestamp',
                                              'description', 'pass_main', 'pass_supp',
                                              'guild_id', 'use_support', 'signup_id'],
                                      where=f'id={id}')
        if record:
            for type in Event._registered_events:
                if type.type() == record['event_type']:
                    self.base = type
                    break
            self.id = id
            self._pl_post_id = record['pl_post_id']
            self._time = record['timestamp']
            self._description = record['description']
            self.passcode_main = record['pass_main']
            self.passcode_supp = record['pass_supp']
            self.guild_id = record['guild_id']
            self._use_support = type.use_support() and record['use_support']
            self.signup.load(record['signup_id'])
            self.users.load(id)

    @property
    def real_description(self) -> str:
        return self._description

    @property
    def description(self) -> str:
        if self.is_signup:
            return self.signup.template.description
        if self.base.category == EventCategory.CUSTOM:
            return self._description
        else:
            return self.base.description()

    @description.setter
    def description(self, value: str) -> None:
        if value == self._description: return
        SQL('events').update(Record(description=value), f'id={self.id}')
        self.load(self.id)

    @property
    def short_description(self) -> str:
        if self.is_signup:
            return self.signup.template.short_description
        return self.base.short_description()

    @property
    def time(self) -> datetime:
        return self._time

    @time.setter
    def time(self, value: datetime) -> None:
        if value == self.auto_passcode: return
        SQL('events').update(Record(timestamp=value), f'id={self.id}')
        self.load(self.id)

    @property
    def auto_passcode(self) -> bool:
        return self.passcode_main != 0 and self.passcode_supp != 0

    @auto_passcode.setter
    def auto_passcode(self, value: bool) -> None:
        if value == self.auto_passcode: return
        if value:
            SQL('events').update(Record(pass_main=EventPasscodeGenerator.generate(),
                                        pass_supp=EventPasscodeGenerator.generate()),
                                 f'id={self.id}')
        else:
            SQL('events').update(Record(pass_main=0, pass_supp=0),
                                 f'id={self.id}')
        self.load(self.id)

    @property
    def dm_title(self) -> str:
        if self.is_signup:
            return self.signup.template.dm_title.replace(
                '%servertime', f'{self.time.strftime("%A, %d-%b-%y %H:%M")}').replace(
                '%localtime', get_discord_timestamp(self.time)).replace(
                '%description', self.signup.template.description)
        return self.base.dm_title(time=self.time)

    @property
    def raid_leader_dm_text(self) -> str:
        if self.is_signup:
            template = self.signup.template.raid_leader_dm_text
            if '%support' in template and self.signup.template.use_support:
                no_support_text = template[template.find('%!support=') + 10:]
                support_text = template[template.find('%support=') + 10:template.find('%!support=')]
                template = template[:template.find('%support=')]
                if not self.use_support: support_text = no_support_text
            else:
                support_text = ''
            return template.replace(
                '%passcode', str(self.passcode_main).zfill(4)).replace(
                '%support', support_text.strip(' \n')).replace(
                '%passcode_support', str(self.passcode_supp).zfill(4))
        return self.base.raid_leader_dm_text(
            passcode_main=self.passcode_main,
            passcode_supp=self.passcode_supp,
            use_support=self.use_support)

    @property
    def use_support(self) -> bool:
        return self._use_support

    @use_support.setter
    def use_support(self, value: bool) -> None:
        if (value == self._use_support) or not self.base.use_support() or (
            self.is_signup and not self.signup.template.use_support): return
        SQL('events').update(Record(use_support=value), f'id={self.id}')
        self.load(self.id)

    @property
    def use_pl_posts(self) -> str:
        if self.is_signup:
            return self.signup.template.use_recruitment_posts
        return self.base.use_pl_posts()

    @property
    def delete_pl_posts(self) -> str:
        if self.is_signup:
            return self.signup.template.delete_recruitment_posts
        return self.base.delete_pl_posts()

    @property
    def support_party_leader_dm_text(self) -> str:
        if self.is_signup:
            return self.signup.template.support_party_leader_dm_text.replace(
                '%passcode', str(self.passcode_supp).zfill(4))
        return self.base.support_party_leader_dm_text(passcode=self.passcode_supp)

    @property
    def schedule_entry_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        if self.is_signup:
            template = self.signup.template.schedule_entry_text
            if '%support' in template and self.signup.template.use_support:
                no_support_text = template[template.find('%!support=') + 10:]
                support_text = template[template.find('%support=') + 10:template.find('%!support=')]
                template = template[:template.find('%support=')]
                if not self.use_support: support_text = no_support_text
            else:
                support_text = ''
            return template.replace(
                '%servertime', f'{self.time.strftime("%H:%M")}').replace(
                "$rl", user.mention).replace(
                '%localtime', get_discord_timestamp(self.time)).replace(
                '%description', self.signup.template.description).replace(
                '%support', support_text.strip(' \n'))
        return self.base.schedule_entry_text(user.mention, self.time, self.real_description, self._use_support)

    @property
    def category(self) -> EventCategory:
        if self.is_signup:
            return EventCategory(self.signup.template.category)
        return self.base.category()

    @property
    def type(self) -> str:
        return self.base.type()

    @type.setter
    def type(self, value: str):
        if value == self.type: return
        if self.is_signup: raise Exception('Cannot change type of a signup event.')
        SQL('events').update(Record(event_type=value), f'id={self.id}')
        self.load(self.id)

    @property
    def use_pl_post_thread(self) -> str:
        if self.is_signup:
            return self.signup.template.use_recruitment_post_thread
        return self.base.use_pl_post_thread()

    @property
    def pl_post_thread_title(self) -> str:
        if self.is_signup:
            return self.signup.template.recruitment_post_thread_title.replace(
                '%time', f'{self.time.strftime("%A, %d-%b-%y %H:%M")}').replace(
                '%description', self.signup.template.description)
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
        if self.is_signup:
            result = self.signup.template.pl_button_texts
        if not self.use_support:
            result_list = list(result)
            result_list[6] = ''
            result = tuple(result_list)
        return result

    @property
    def pl_post_title(self) -> str:
        if self.is_signup:
            return self.signup.template.recruitment_post_title.replace(
                '%servertime', f'{self.time.strftime("%A, %d-%b-%y %H:%M")}').replace(
                "%localtime", get_discord_timestamp(self.time)).replace(
                '%description', self.signup.template.description)
        return self.base.pl_post_title(self.time)

    @property
    def pl_passcode_delay(self) -> timedelta:
        if self.is_signup:
            return timedelta(minutes=self.signup.template.passcode_delay)
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
        if self.is_signup:
            return self.signup.template.recruitment_post_text

        guild = bot.instance.get_guild(self.guild_id)
        rl = guild.get_member(self.users.raid_leader)
        pl1 = self._pl_placeholder(guild.get_member(self.users.party_leaders[0])) if self.base.pl_button_texts()[0] else None
        pl2 = self._pl_placeholder(guild.get_member(self.users.party_leaders[1])) if self.base.pl_button_texts()[1] else None
        pl3 = self._pl_placeholder(guild.get_member(self.users.party_leaders[2])) if self.base.pl_button_texts()[2] else None
        pl4 = self._pl_placeholder(guild.get_member(self.users.party_leaders[3])) if self.base.pl_button_texts()[3] else None
        pl5 = self._pl_placeholder(guild.get_member(self.users.party_leaders[4])) if self.base.pl_button_texts()[4] else None
        pl6 = self._pl_placeholder(guild.get_member(self.users.party_leaders[5])) if self.base.pl_button_texts()[5] else None
        pls = self._pl_placeholder(guild.get_member(self.users.party_leaders[6])) if self.use_support else None

        return self.base.pl_post_text(rl.mention, pl1, pl2, pl3, pl4, pl5, pl6, pls)

    def party_leader_dm_text(self, index: int) -> str:
        if self.is_signup:
            return self.signup.template.party_leader_dm_text.replace(
                '%party', self.pl_button_texts[index]).replace(
                '%passcode', str(self.passcode_main).zfill(4))
        return self.base.party_leader_dm_text(
            party=self.pl_button_texts[index],
            passcode=self.passcode_main)

    @property
    def pl_post_id(self) -> int:
        return self._pl_post_id

    @pl_post_id.setter
    def pl_post_id(self, value: int) -> None:
        SQL('events').update(Record(pl_post_id=value), f'id={self.id}')
        self.load(self.id)

    @property
    def is_signup(self) -> bool:
        return not self.signup.id is None and self.signup.id > 0

    def dm_text(self, index: int) -> str:
        passcode = self.passcode_main if index < 6 else self.passcode_supp
        if self.is_signup:
            return self.signup.template.dm_text.replace(
                '%party', self.pl_button_texts[index]).replace(
                '%passcode', str(passcode).zfill(4))
        return self.base.dm_text(
            party=self.pl_button_texts[index],
            passcode=passcode)

    def create_tasks(self) -> None:
        bot.instance.data.tasks.add_task(self.time, TaskExecutionType.REMOVE_OLD_RUNS, {"id": self.id})
        if self.use_pl_posts and self.delete_pl_posts:
            channel_data = bot.instance.data.guilds.get(self.guild_id).channels.get(GuildChannelFunction.PL_CHANNEL, self.type)
            if channel_data:
                bot.instance.data.tasks.add_task(self.time + timedelta(hours=12), TaskExecutionType.REMOVE_OLD_MESSAGE, {"guild": self.guild_id, "message_id": self.pl_post_id})
        if not self.auto_passcode: return
        if not self.is_signup:
            bot.instance.data.tasks.add_task(self.time - self.main_passcode_delay, TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        bot.instance.data.tasks.add_task(self.time - self.pl_passcode_delay, TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild_id, "entry_id": self.id})
        if self.use_support and not self.is_signup:
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

    def get_changes(self, interaction: Interaction, old_event: Type['ScheduledEvent']) -> str:
        result = []
        if self.type != old_event.type:
            result.append(f'* Run Type changed from {old_event.base.short_description()} to {self.base.short_description()}')
        if self.time != old_event.time:
            result.append(f'* Run Time changed from {old_event.time} ST to {self.time} ST')
        if self.users.raid_leader != old_event.users.raid_leader:
            result.append(f'* Raid Leader changed from {interaction.guild.get_member(old_event.users.raid_leader).mention} to {interaction.guild.get_member(self.users.raid_leader).mention}')
        if self.auto_passcode != old_event.auto_passcode:
            result.append(f'* Auto Passcode changed from {str(old_event.auto_passcode)} to {str(self.auto_passcode)}')
        if self.use_support != old_event.use_support:
            result.append(f'* Use Support changed from {str(old_event.use_support)} to {str(self.use_support)}')
        if self.real_description != old_event.real_description:
            result.append(f'* Description changed from "{old_event.real_description}" to "{self.real_description}"')
        if not result:
            result.append('No changes.')
        return "\n".join(result)

