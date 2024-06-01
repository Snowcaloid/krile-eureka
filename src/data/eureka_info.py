from datetime import datetime
from enum import Enum
import bot
from typing import List

from data.db.database import pg_timestamp


class EurekaTrackerZone(Enum):
    ANEMOS = 1
    PAGOS = 2
    PYROS = 3
    HYDATOS = 4


class EurekaTracker:
    def load(self, url: str) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.url = url
            for record in db.query(f"select zone, timestamp from trackers where url='{url}'"):
                self.zone = EurekaTrackerZone(record[0])
                self.timestamp: datetime = record[1]
        finally:
            db.disconnect()


class EurekaInfo:
    _trackers: List[EurekaTracker] = []

    def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self._trackers.clear()
            records = db.query(f'select url from trackers')
            for record in records:
                tracker = EurekaTracker()
                tracker.load(record[0])
                self._trackers.append(tracker)
        finally:
            db.disconnect()

    def get(self, zone: EurekaTrackerZone) -> List[EurekaTracker]:
        return [tracker for tracker in self._trackers if tracker.zone == zone]

    def add(self, url: str, zone: EurekaTrackerZone) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f"insert into trackers (url, zone, timestamp) values ('{url}', {str(zone.value)}, {pg_timestamp(datetime.utcnow())})")
            self.load()
        finally:
            db.disconnect()

    def remove(self, url: str) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            # delete trackers older than 4 hours
            db.query(f"delete from trackers where url='{url}'")
            self.load()
        finally:
            db.disconnect()

    def remove_old(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            # delete trackers older than 4 hours
            db.query(f'delete from trackers where extract(epoch from {pg_timestamp(datetime.utcnow())}-timestamp)/3600 > 4')
            self.load()
        finally:
            db.disconnect()