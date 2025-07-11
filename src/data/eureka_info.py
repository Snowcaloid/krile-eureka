from datetime import datetime
from typing import List

from centralized_data import Bindable

from utils.basic_types import EurekaInstance
from data.db.database import pg_timestamp
from data.db.sql import _SQL, Record


class EurekaTracker:
    def load(self, url: str) -> None:
        self.url = url
        for record in _SQL('trackers').select(fields=['zone', 'timestamp'], where=f'url=\'{url}\'', all=True):
            self.zone = EurekaInstance(record['zone'])
            self.timestamp: datetime = record['timestamp']


class EurekaInfo(Bindable):
    def constructor(self) -> None:
        super().constructor()
        self._trackers: List[EurekaTracker] = []
        self.load()

    def load(self) -> None:
        self._trackers.clear()
        for record in _SQL('trackers').select(fields=['url']):
            tracker = EurekaTracker()
            tracker.load(record['url'])
            self._trackers.append(tracker)

    def get(self, zone: EurekaInstance) -> List[EurekaTracker]:
        return [tracker for tracker in self._trackers if tracker.zone == zone]

    def add(self, url: str, zone: EurekaInstance) -> None:
        _SQL('trackers').insert(Record(url=url, zone=zone.value, timestamp=datetime.utcnow()))
        self.load()

    def remove(self, url: str) -> None:
        _SQL('trackers').delete(f"url='{url}'")
        self.load()

    def remove_old(self) -> None:
        # delete trackers older than 4 hours
        _SQL('trackers').delete(f"extract(epoch from {pg_timestamp(datetime.utcnow())}-timestamp)/3600 > 4")
        self.load()