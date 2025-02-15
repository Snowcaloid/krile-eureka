
from discord import Interaction, Member
import bot
from indexedproperty import indexedproperty
from datetime import datetime, timedelta
from typing import List, Tuple, Type
from data.db.sql import SQL, Record
from data.events.event_template import EventCategory, EventTemplate
from data.generators.event_passcode_generator import EventPasscodeGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.tasks.tasks import TaskExecutionType

from utils import DiscordTimestampType, get_discord_member, get_discord_timestamp

PL_FIELDS = ['pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'pl6', 'pls']

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
    template: EventTemplate
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
        record = SQL('events').select(fields=['event_type', 'pl_post_id', 'timestamp',
                                              'description', 'pass_main', 'pass_supp',
                                              'guild_id', 'use_support'],
                                      where=f'id={id}')
        if record:
            self.id = id
            self._pl_post_id = record['pl_post_id']
            self._time = record['timestamp']
            self._description = record['description']
            self.passcode_main = record['pass_main']
            self.passcode_supp = record['pass_supp']
            self.guild_id = record['guild_id']
            self.template = bot.instance.data.guilds.get(self.guild_id).event_templates.get(record['event_type'])
            self._use_support = self.template.use_support() and record['use_support']
            self.users.load(id)

    @property
    def real_description(self) -> str:
        return self._description

    @property
    def description(self) -> str:
        if self.template.category == EventCategory.CUSTOM:
            return self._description
        else:
            return self.template.description()

    @description.setter
    def description(self, value: str) -> None:
        if value == self._description: return
        SQL('events').update(Record(description=value), f'id={self.id}')
        self.load(self.id)

    @property
    def short_description(self) -> str:
        return self.template.short_description()

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
        return self.template.dm_title(time=self.time)

    @property
    def raid_leader_dm_text(self) -> str:
        return self.template.raid_leader_dm_text(
            passcode_main=self.passcode_main,
            passcode_supp=self.passcode_supp,
            use_support=self.use_support)

    @property
    def use_support(self) -> bool:
        return self._use_support

    @use_support.setter
    def use_support(self, value: bool) -> None:
        if (value == self._use_support) or not self.template.use_support(): return
        SQL('events').update(Record(use_support=value), f'id={self.id}')
        self.load(self.id)

    @property
    def use_recruitment_posts(self) -> str:
        return self.template.use_recruitment_posts()

    @property
    def delete_recruitment_posts(self) -> str:
        return self.template.delete_recruitment_posts()

    @property
    def support_party_leader_dm_text(self) -> str:
        return self.template.support_party_leader_dm_text(passcode=self.passcode_supp)

    @property
    def schedule_entry_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.template.schedule_entry_text(user.mention, self.time, self.real_description, self._use_support)

    @property
    def category(self) -> EventCategory:
        return self.template.category()

    @property
    def type(self) -> str:
        return self.template.type()

    @type.setter
    def type(self, value: str):
        if value == self.type: return
        SQL('events').update(Record(event_type=value), f'id={self.id}')
        self.load(self.id)

    @property
    def use_recruitment_post_threads(self) -> str:
        return self.template.use_recruitment_post_threads()

    @property
    def recruitment_post_thread_title(self) -> str:
        return self.template.recruitment_post_thread_title(self.time)

    @property
    def main_passcode_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.template.main_passcode_text(user.mention, self.passcode_main)

    @property
    def support_passcode_text(self) -> str:
        user = bot.instance.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.template.support_passcode_text(user.mention, self.passcode_supp)

    @property
    def passcode_post_title(self) -> str:
        return self.template.passcode_post_title(self.time)

    @property
    def pl_button_texts(self) -> Tuple[str, str, str, str, str, str, str]:
        result = self.template.pl_button_texts()
        if not self.use_support:
            result_list = list(result)
            result_list[6] = ''
            result = tuple(result_list)
        return result

    @property
    def recruitment_post_title(self) -> str:
        return self.template.recruitment_post_title(self.time)

    @property
    def pl_passcode_delay(self) -> timedelta:
        return self.template.pl_passcode_delay()

    @property
    def main_passcode_delay(self) -> timedelta:
        return self.template.main_passcode_delay()

    @property
    def support_passcode_delay(self) -> timedelta:
        return self.template.support_passcode_delay()

    def _pl_placeholder(self, member: Member) -> str:
        return member.display_name if member else 'TBD'

    @property
    def recruitment_post_text(self) -> str:
        guild = bot.instance.get_guild(self.guild_id)
        rl = guild.get_member(self.users.raid_leader)
        pl1 = self._pl_placeholder(guild.get_member(self.users.party_leaders[0])) if self.template.pl_button_texts()[0] else None
        pl2 = self._pl_placeholder(guild.get_member(self.users.party_leaders[1])) if self.template.pl_button_texts()[1] else None
        pl3 = self._pl_placeholder(guild.get_member(self.users.party_leaders[2])) if self.template.pl_button_texts()[2] else None
        pl4 = self._pl_placeholder(guild.get_member(self.users.party_leaders[3])) if self.template.pl_button_texts()[3] else None
        pl5 = self._pl_placeholder(guild.get_member(self.users.party_leaders[4])) if self.template.pl_button_texts()[4] else None
        pl6 = self._pl_placeholder(guild.get_member(self.users.party_leaders[5])) if self.template.pl_button_texts()[5] else None
        pls = self._pl_placeholder(guild.get_member(self.users.party_leaders[6])) if self.use_support else None

        return self.template.recruitment_post_text(rl.mention, pl1, pl2, pl3, pl4, pl5, pl6, pls)

    def party_leader_dm_text(self, index: int) -> str:
        return self.template.party_leader_dm_text(
            party=self.pl_button_texts[index],
            passcode=self.passcode_main)

    @property
    def pl_post_id(self) -> int:
        return self._pl_post_id

    @pl_post_id.setter
    def pl_post_id(self, value: int) -> None:
        SQL('events').update(Record(pl_post_id=value), f'id={self.id}')
        self.load(self.id)

    def create_tasks(self) -> None:
        bot.instance.data.tasks.add_task(self.time, TaskExecutionType.REMOVE_OLD_RUNS, {"id": self.id})
        if self.use_recruitment_posts and self.delete_recruitment_posts:
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
        return f'{self.template.short_description()} by {raid_leader.display_name} at {self.time} ST {discord_timestamp}'

    def get_changes(self, interaction: Interaction, old_event: Type['ScheduledEvent']) -> str:
        result = []
        if self.type != old_event.type:
            result.append(f'* Run Type changed from {old_event.template.short_description()} to {self.template.short_description()}')
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

