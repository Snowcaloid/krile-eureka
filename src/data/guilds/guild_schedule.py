from datetime import datetime
import bot
from typing import List
from data.db.database import pg_timestamp
from data.events.event import ScheduledEvent
from data.generators.event_passcode_generator import EventPasscodeGenerator


class GuildSchedule:
    _list: List[ScheduledEvent] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self._list.clear()
            records = db.query(f'select id from events where guild_id={self.guild_id} and (not finished or finished is null) and (not canceled or canceled is null)')
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
            description: str = '', auto_passcode: bool = True,
            use_support: bool = True) -> ScheduledEvent:
        db = bot.instance.data.db
        db.connect()
        try:
            description = description.replace('\'', '\'\'')
            pass_main = EventPasscodeGenerator.generate() if auto_passcode else 0
            pass_supp = EventPasscodeGenerator.generate() if auto_passcode else 0
            id = db.query((
                'insert into events (guild_id, raid_leader, event_type, timestamp, description, pass_main, pass_supp, use_support) '
                f'values ({self.guild_id}, {leader}, \'{event_type}\', {pg_timestamp(time)}, '
                f'\'{description}\', {str(pass_main)}, {str(pass_supp)}, {use_support}) returning id'
            ))
            self.load(self.guild_id)
            result = self.get(id)
            return result
        finally:
            db.disconnect()

    def edit(self, id: int, leader: int, event_type: str, datetime: datetime, description: str,
             auto_passcode: bool, use_support: bool) -> ScheduledEvent:
        event = self.get(id)
        if event.time != datetime:
            event.time = datetime
        if not auto_passcode is None and event.auto_passcode != auto_passcode:
            event.auto_passcode = auto_passcode
        if not leader is None:
            event.users.raid_leader = leader
        if not event_type is None:
            event.type = event_type
        if description:
            event.description = description
        if event.base.use_support() and (use_support != event.use_support):
            event.use_support = use_support
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