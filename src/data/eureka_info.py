from datetime import datetime
from typing import List

from centralized_data import Bindable

from basic_types import EurekaTrackerZone
from data.db.database import pg_timestamp
from data.db.sql import SQL, Record


class EurekaTracker:
    def load(self, url: str) -> None:
        self.url = url
        for record in SQL('trackers').select(fields=['zone', 'timestamp'], where=f'url=\'{url}\'', all=True):
            self.zone = EurekaTrackerZone(record['zone'])
            self.timestamp: datetime = record['timestamp']


class EurekaInfo(Bindable):
    def constructor(self) -> None:
        super().constructor()
        self._trackers: List[EurekaTracker] = []

    def load(self) -> None:
        self._trackers.clear()
        for record in SQL('trackers').select(fields=['url']):
            tracker = EurekaTracker()
            tracker.load(record['url'])
            self._trackers.append(tracker)

    def get(self, zone: EurekaTrackerZone) -> List[EurekaTracker]:
        return [tracker for tracker in self._trackers if tracker.zone == zone]

    def add(self, url: str, zone: EurekaTrackerZone) -> None:
        SQL('trackers').insert(Record(url=url, zone=zone.value, timestamp=datetime.utcnow()))
        self.load()

    def remove(self, url: str) -> None:
        SQL('trackers').delete(f"url='{url}'")
        self.load()

    def remove_old(self) -> None:
        # delete trackers older than 4 hours
        SQL('trackers').delete(f"extract(epoch from {pg_timestamp(datetime.utcnow())}-timestamp)/3600 > 4")
        self.load()