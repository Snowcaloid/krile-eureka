from dataclasses import dataclass
from centralized_data import GlobalCollection
from utils.basic_types import GuildID
from data.db.sql import SQL, Record, in_transaction
from data.events.event import Event
from data.generators.event_passcode_generator import EventPasscodeGenerator

from datetime import datetime
from typing import List

@dataclass
class EventLike(dict):
    """
        # Keys
        * event_type: str
        * raid_leader: int
        * time: datetime
        * description: str `optional`
        * auto_passcode: bool `optional`
        * use_support: bool `optional`
    """
    ...


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

    @in_transaction
    def add(self, event: EventLike) -> Event:
        if event.pop("description", None) is not None:
            description = event.description.replace('\'', '\'\'')
        auto_passcode = event.pop("auto_passcode", None)
        pass_main = EventPasscodeGenerator.generate() if auto_passcode else 0
        pass_supp = EventPasscodeGenerator.generate() if auto_passcode else 0
        id = SQL('events').insert(Record(
                guild_id=self.key,
                raid_leader=event.pop("raid_leader", None),
                event_type=event.pop("event_type", None),
                timestamp=event.pop("timestamp", None),
                description=description,
                pass_main=pass_main,
                pass_supp=pass_supp,
                use_support=event.pop("use_support", None) or False
            ),
            'id')
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
       return self._list