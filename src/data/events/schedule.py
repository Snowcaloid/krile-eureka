from copy import deepcopy
from dataclasses import dataclass
from centralized_data import GlobalCollection
from utils.basic_types import GuildID, TaskExecutionType
from data.db.sql import SQL, Record
from data.events.event import Event

from datetime import datetime
from typing import List

from utils.discord_types import InteractionLike
from utils.functions import generate_passcode

@dataclass
class EventLike(dict):
    """
        # Keys
        * event_type: str
        * raid_leader: int
        * datetime: datetime
        * description: str `optional`
        * auto_passcode: bool `optional`
        * use_support: bool `optional`
    """
    ...


class Schedule(GlobalCollection[GuildID]):
    _list: List[Event]

    from tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

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

    def add(self, event: EventLike, interaction: InteractionLike) -> Event:
        auto_passcode = event.pop("auto_passcode", None)
        pass_main = generate_passcode() if auto_passcode else 0
        pass_supp = generate_passcode(False) if auto_passcode else 0
        id = SQL('events').insert(Record(
                guild_id=self.key,
                raid_leader=event.pop("raid_leader")["id"],
                event_type=event.pop("type"),
                timestamp=event.pop("datetime"),
                description=event.pop("description", None),
                pass_main=pass_main,
                pass_supp=pass_supp,
                use_support=event.pop("use_support", None) or False
            ),
            'id')
        self.load()
        result = self.get(id)
        self.tasks.add_task(datetime.utcnow(), TaskExecutionType.EVENT_UPDATE,
                            { 'event': result, 'interaction': interaction })
        return result

    def edit(self, id: int, model: dict, interaction: InteractionLike) -> Event:
        event = self.get(id)
        old_event = deepcopy(event)
        event.unmarshal(model)
        self.tasks.add_task(datetime.utcnow(), TaskExecutionType.EVENT_UPDATE,
                            { 'event': event, 'changes': model, 'interaction': interaction, 'old_event': old_event })
        return event

    def finish(self, event_id: int):
        SQL('events').update(Record(finished=True), f'id={event_id}')
        self.load()

    def cancel(self, event_id: int, interaction: InteractionLike) -> None:
        event = self.get(event_id)
        SQL('events').update(Record(canceled=True), f'id={event_id}')
        self.load()
        self.tasks.add_task(datetime.utcnow(), TaskExecutionType.EVENT_CANCEL,
                            { 'event': event, 'guild': self.key, 'interaction': interaction })

    def contains(self, event_id: int) -> bool:
        return not self.get(event_id) is None

    @property
    def all(self) -> List[Event]:
       return self._list