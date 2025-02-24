from centralized_data import GlobalCollection
from basic_types import GuildID
from data.db.sql import SQL, Record
from data.events.event import Event
from data.generators.event_passcode_generator import EventPasscodeGenerator

from datetime import datetime
from typing import List

class Schedule(GlobalCollection[GuildID]):
    _list: List[Event]

    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('events').select(fields=['id'],
                                           where=f'guild_id = {self.key} and (not finished or finished is null) and (not canceled or canceled is null)',
                                           all=True):
            event = Event()
            event.load(record['id'])
            self._list.append(event)

    def get(self, event_id: int) -> Event:
        return next(event for event in self._list if event.id == event_id)

    def add(self, leader: int, event_type: str, time: datetime,
            description: str = '', auto_passcode: bool = True,
            use_support: bool = True) -> Event:
        description = description.replace('\'', '\'\'')
        pass_main = EventPasscodeGenerator.generate() if auto_passcode else 0
        pass_supp = EventPasscodeGenerator.generate() if auto_passcode else 0
        id = SQL('events').insert(Record(guild_id=self.key,
                                         raid_leader=leader,
                                         event_type=event_type,
                                         timestamp=time,
                                         description=description,
                                         pass_main=pass_main,
                                         pass_supp=pass_supp,
                                         use_support=use_support),
                                  returning_field='id')
        self.load()
        result = self.get(id)
        return result

    def edit(self, id: int, leader: int, event_type: str, datetime: datetime, description: str,
             auto_passcode: bool, use_support: bool) -> Event:
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
        if event.template.use_support() and (use_support != event.use_support):
            event.use_support = use_support
        return event

    def finish(self, event_id: int):
        SQL('events').update(Record(finished=True), f'id={event_id}')
        self.load()

    def cancel(self, event_id: int):
        SQL('events').update(Record(canceled=True), f'id={event_id}')
        self.load()

    def contains(self, event_id: int) -> bool:
        return not self.get(event_id) is None

    @property
    def all(self) -> List[Event]:
        return [event for event in self._list if event.guild_id == self.key]