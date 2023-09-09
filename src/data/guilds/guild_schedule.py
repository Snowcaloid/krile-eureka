from datetime import datetime
import bot
from typing import List
from data.db.database import pg_timestamp
from data.events.event import ScheduledEvent
from data.generators.event_passcode_generator import EventPasscodeGenerator

class GuildSchedulePost:
    guild_id: int
    id: int
    channel: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            record = db.query(f'select schedule_post, schedule_channel from guilds where guild_id={guild_id}')
            if record and record[0]:
                self.id = record[0][0]
                self.channel = record[0][1]
        finally:
            db.disconnect()

    def set(self, id: int, channel: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update guilds set schedule_post={id}, schedule_channel={channel} where guild_id={self.guild_id}')
            self.load(self.guild_id)
        finally:
            db.disconnect()


class GuildSchedule:
    _list: List[ScheduledEvent] = []
    schedule_post: GuildSchedulePost

    guild_id: int

    def __init__(self):
        self.schedule_post = GuildSchedulePost()

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self.schedule_post.load(guild_id)
            self._list.clear()
            if self.schedule_post.id:
                records = db.query(f'select id from events where guild_id={self.guild_id}')
                for record in records:
                    event = ScheduledEvent()
                    event.load(record[0])
                    self._list.append(event)
        finally:
            db.disconnect()

    def get(self, event_id: int) -> ScheduledEvent:
        for event in self._list:
            if event.id == event_id:
                return event
        return None

    def add(self, leader: int, event_type: str, time: datetime,
            description: str = '', auto_passcode: bool = True) -> ScheduledEvent:
        db = bot.instance.data.db
        db.connect()
        try:
            description = description.replace('\'', '\'\'')
            pass_main = EventPasscodeGenerator.generate() if auto_passcode else 0
            pass_supp = EventPasscodeGenerator.generate() if auto_passcode else 0
            id = db.query((
                'insert into events (guild_id, raid_leader, event_type, timestamp, description, pass_main, pass_supp) '
                f'values ({self.guild_id}, {leader}, \'{event_type}\', {pg_timestamp(time)}, '
                f'\'{description}\', {str(pass_main)}, {str(pass_supp)}) returning id'
            ))
            self.load(self.guild_id)
            result = self.get(id)
            result.create_tasks()
            return result
        finally:
            db.disconnect()

    def edit(self, id: int, leader: int, event_type: str, datetime: datetime, description: str,
             auto_passcode: bool) -> ScheduledEvent:
        event = self.get(id)
        is_time_update = event.time != datetime
        if is_time_update:
            event.time = datetime
        is_passcode_update = not auto_passcode is None and event.auto_passcode != auto_passcode
        if is_passcode_update:
            event.auto_passcode = auto_passcode
        if not leader is None:
            event.users.raid_leader = leader
        if not event_type is None:
            event.type = event_type
        if description:
            event.description = description
        if is_passcode_update or is_time_update:
            event.delete_tasks()
            event.create_tasks()
        return event

    def finish(self, event_id: int):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set finished=true where id={event_id}')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def cancel(self, event_id: int):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update events set canceled=true where id={event_id}')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def contains(self, event_id: int) -> bool:
        return not self.get(event_id) is None

    @property
    def all(self) -> List[ScheduledEvent]:
        return self._list