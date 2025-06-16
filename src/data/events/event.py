
from utils.basic_types import EventCategory
from discord import Interaction, Member
from indexedproperty import indexedproperty
from datetime import datetime, timedelta
from typing import List, Tuple, Type
from data.db.sql import _SQL, Record, Transaction
from models.event_template.data import EventTemplateData
from data.events.event_templates import EventTemplates
from utils.basic_types import ChannelFunction
from utils.basic_types import TaskExecutionType

from utils.functions import DiscordTimestampType, generate_passcode, get_discord_timestamp, user_display_name

class EventUserData:
    event_id: int
    _raid_leader: int
    _party_leaders: List[int]

    def load(self, event_id: int) -> None:
        self.event_id = event_id
        record = _SQL('events').select(fields=['raid_leader', 'pl1', 'pl2', 'pl3',
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
        _SQL('events').update(Record(raid_leader=value), f'id={self.event_id}')
        self.load(self.event_id)

    @indexedproperty
    def party_leaders(self, index: int) -> int:
        return self._party_leaders[index]

    @party_leaders.setter
    def party_leaders(self, index: int, value: int) -> None:
        record = Record()
        record[PL_FIELDS[index]] = value
        _SQL('events').update(record, f'id={self.event_id}')
        self.load(self.event_id)

PL_FIELDS = ['pl1', 'pl2', 'pl3', 'pl4', 'pl5', 'pl6', 'pls']

class Event:
    template: EventTemplateData
    id: int
    _recruitment_post: int
    _time: datetime
    guild_id: int
    users: EventUserData
    passcode_main: int
    passcode_supp: int
    _description: str
    _use_support: bool

    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from tasks import Tasks
    @Tasks.bind
    def _tasks(self) -> Tasks: ...

    def __init__(self):
        self.users = EventUserData()

    def load(self, id: int) -> None:
        record = _SQL('events').select(fields=['event_type', 'pl_post_id', 'timestamp',
                                              'description', 'pass_main', 'pass_supp',
                                              'guild_id', 'use_support'],
                                      where=f'id={id}')
        if record:
            self.id = id
            self._recruitment_post = record['pl_post_id']
            self._time = record['timestamp']
            self._description = record['description']
            self.passcode_main = record['pass_main']
            self.passcode_supp = record['pass_supp']
            self.guild_id = record['guild_id']
            self.template = EventTemplates(self.guild_id).get(record['event_type'])
            self._use_support = self.template.use_support() and record['use_support']
            self.users.load(id)

    def marshal(self) -> dict:
        return {
            "id": self.id,
            "type": self.template.type(),
            "guild_id": self.guild_id,
            "datetime": self.time,
            "description": self.real_description,
            "raid_leader": {
                "id": self.users._raid_leader,
                "name": user_display_name(self.guild_id, self.users._raid_leader)
            },
            "party_leaders": [ {
                "id": leader,
                "name": user_display_name(self.guild_id, leader)
            } for leader in self.users._party_leaders ],
            "use_support": self.use_support,
            "pass_main": self.passcode_main,
            "pass_supp": self.passcode_supp,
            "auto_passcode": self.auto_passcode
        }

    def unmarshal(self, model: dict) -> None:
        with Transaction():
            if 'type' in model:
                self.template = EventTemplates(self.guild_id).get(model['type'])
            if 'datetime' in model:
                self.time = model['datetime']
            if 'description' in model:
                self.real_description = model['description']
            if 'raid_leader' in model:
                self.users.raid_leader = model['raid_leader']['id']
            if 'party_leaders' in model:
                for i in range(7):
                    self.users.party_leaders[i] = model['party_leaders'][i]['id']
            if 'use_support' in model:
                self.use_support = model['use_support']
            if 'auto_passcode' in model:
                self.auto_passcode = model['auto_passcode']

    @property
    def real_description(self) -> str:
        return self._description

    @property
    def description(self) -> str:
        if self.template.category() == EventCategory.CUSTOM:
            return self._description
        else:
            return self.template.description()

    @description.setter
    def description(self, value: str) -> None:
        if value == self._description: return
        _SQL('events').update(Record(description=value), f'id={self.id}')
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
        _SQL('events').update(Record(timestamp=value), f'id={self.id}')
        self.load(self.id)

    @property
    def auto_passcode(self) -> bool:
        return self.passcode_main != 0 and self.passcode_supp != 0

    @auto_passcode.setter
    def auto_passcode(self, value: bool) -> None:
        if value == self.auto_passcode: return
        if value:
            _SQL('events').update(Record(pass_main=generate_passcode(),
                                        pass_supp=generate_passcode(False)),
                                 f'id={self.id}')
        else:
            _SQL('events').update(Record(pass_main=0, pass_supp=0),
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
        _SQL('events').update(Record(use_support=value), f'id={self.id}')
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
        user = self.bot._client.get_guild(self.guild_id).get_member(self.users.raid_leader)
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
        _SQL('events').update(Record(event_type=value), f'id={self.id}')
        self.load(self.id)

    @property
    def use_recruitment_post_threads(self) -> str:
        return self.template.use_recruitment_post_threads()

    @property
    def recruitment_post_thread_title(self) -> str:
        return self.template.recruitment_post_thread_title(self.time)

    @property
    def main_passcode_text(self) -> str:
        user = self.bot._client.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.template.main_passcode_text(user.mention, self.passcode_main)

    @property
    def support_passcode_text(self) -> str:
        user = self.bot._client.get_guild(self.guild_id).get_member(self.users.raid_leader)
        return self.template.support_passcode_text(user.mention, self.passcode_supp)

    @property
    def passcode_post_title(self) -> str:
        return self.template.passcode_post_title(self.time)

    @property
    def pl_button_texts(self) -> Tuple[str, str, str, str, str, str, str]:
        result = self.template.party_descriptions()
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
        guild = self.bot._client.get_guild(self.guild_id)
        rl = guild.get_member(self.users.raid_leader)
        pl1 = self._pl_placeholder(guild.get_member(self.users.party_leaders[0])) if self.template.party_descriptions()[0] else ''
        pl2 = self._pl_placeholder(guild.get_member(self.users.party_leaders[1])) if self.template.party_descriptions()[1] else ''
        pl3 = self._pl_placeholder(guild.get_member(self.users.party_leaders[2])) if self.template.party_descriptions()[2] else ''
        pl4 = self._pl_placeholder(guild.get_member(self.users.party_leaders[3])) if self.template.party_descriptions()[3] else ''
        pl5 = self._pl_placeholder(guild.get_member(self.users.party_leaders[4])) if self.template.party_descriptions()[4] else ''
        pl6 = self._pl_placeholder(guild.get_member(self.users.party_leaders[5])) if self.template.party_descriptions()[5] else ''
        pls = self._pl_placeholder(guild.get_member(self.users.party_leaders[6])) if self.use_support else ''

        return self.template.recruitment_post_text(rl.mention, pl1, pl2, pl3, pl4, pl5, pl6, pls, self._use_support)

    def party_leader_dm_text(self, index: int) -> str:
        return self.template.party_leader_dm_text(
            party=self.pl_button_texts[index],
            passcode=self.passcode_main)

    @property
    def recruitment_post(self) -> int:
        return self._recruitment_post

    @recruitment_post.setter
    def recruitment_post(self, value: int) -> None:
        _SQL('events').update(Record(pl_post_id=value), f'id={self.id}')
        self.load(self.id)

    def create_tasks(self) -> None:
        self._tasks.add_task(self.time, TaskExecutionType.MARK_RUN_AS_FINISHED, {"id": self.id, "guild": self.guild_id})
        if self.use_recruitment_posts and self.delete_recruitment_posts:
            channel_data = GuildChannels(self.guild_id).get(ChannelFunction.RECRUITMENT, self.type)
            if channel_data:
                self._tasks.add_task(self.time + timedelta(hours=12), TaskExecutionType.REMOVE_RECRUITMENT_POST, {"guild": self.guild_id, "message_id": self.recruitment_post})
        if not self.auto_passcode: return
        self._tasks.add_task(self.time - self.main_passcode_delay, TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        self._tasks.add_task(self.time - self.pl_passcode_delay, TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild_id, "entry_id": self.id})
        if self.use_support:
            self._tasks.add_task(self.time - self.support_passcode_delay, TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})

    def delete_tasks(self) -> None:
        self._tasks.remove_task_by_data(TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild_id, "entry_id": self.id})
        self._tasks.remove_task_by_data(TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        self._tasks.remove_task_by_data(TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild_id, "entry_id": self.id})
        self._tasks.remove_task_by_data(TaskExecutionType.MARK_RUN_AS_FINISHED, {"id": self.id, "guild": self.guild_id})
        self._tasks.remove_task_by_data(TaskExecutionType.REMOVE_RECRUITMENT_POST, {"guild": self.guild_id, "message_id": self.recruitment_post})

    def recreate_tasks(self) -> None:
        self.delete_tasks()
        self.create_tasks()

    def to_string(self) -> str:
        guild = self.bot._client.get_guild(self.guild_id)
        assert guild is not None, "Guild not found"
        raid_leader = guild.get_member(self.users.raid_leader)
        assert raid_leader is not None, "Raid leader not found"
        discord_timestamp = get_discord_timestamp(self.time, DiscordTimestampType.RELATIVE)
        return f'{self.template.short_description()} by {raid_leader.display_name} at {self.time} ST {discord_timestamp}'
