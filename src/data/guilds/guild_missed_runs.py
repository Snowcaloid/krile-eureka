from discord import Member
import bot
from typing import List

from data.guilds.guild_role_functions import GuildRoleFunction


class GuildMissedRunRecord:
    user: int
    event_category: str
    amount: int

class GuildMissedRuns:
    _list: List[GuildMissedRunRecord] = []

    guild_id: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self._list.clear()
            db_records = db.query(f'select user_id, event_category, amount from missed_records where guild_id={guild_id}')
            for db_record in db_records:
                record = GuildMissedRunRecord()
                record.user = db_record[0]
                record.event_category = db_record[1]
                record.amount = db_record[2]
                self._list.append(record)
        finally:
            db.disconnect()

    @property
    def all(self) -> List[GuildMissedRunRecord]:
        return self._list

    def get(self, user: int, event_category: str) -> GuildMissedRunRecord:
        for record in self._list:
            if record.user == user and record.event_category == event_category:
                return record
        return None

    def eligable(self, user: int, event_category: str) -> bool:
        record = self.get(user, event_category)
        return not record is None and record.amount >= 3

    def inc(self, user: int, event_category: str) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            record = self.get(user, event_category)
            if record:
                db.query(f'update missed_records set amount={record.amount + 1} where guild_id={self.guild_id} and user_id={user} and event_category=\'{event_category}\'')
            else:
                db.query(f'insert into missed_records (guild_id, user_id, amount, event_category) values ({self.guild_id}, {user}, {1}, \'{event_category}\')')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def remove(self, user: int, event_category: str):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from missed_records where guild_id={self.guild_id} and user_id={user} and event_category=\'{event_category}\'')
            self.load(self.guild_id)
        finally:
            db.disconnect()
