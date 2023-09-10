from discord import Member
import bot
from typing import List


class GuildMissedRunRecord:
    user: int
    amount: int


class GuildMissedRuns:
    _list: List[GuildMissedRunRecord] = []
    _allowed_roles: List[int] = []
    _blacklisted_roles: List[int] = []

    message_id: int
    guild_id: int

    def load(self, guild_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.guild_id = guild_id
            self._list.clear()
            db_record = db.query(f'select missed_post from guilds where guild_id={guild_id}')
            if db_record:
                self.message_id = db_record[0][0]

            db_records = db.query(f'select user_id, amount from missed_records where guild_id={guild_id}')
            for db_record in db_records:
                record = GuildMissedRunRecord()
                record.user = db_record[0]
                record.amount = db_record[1]
                self._list.append(record)
        finally:
            db.disconnect()

    def assign_message(self, message_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'update guilds set missed_post={str(message_id)} where guild_id={self.guild_id}')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    @property
    def all(self) -> List[GuildMissedRunRecord]:
        return self._list

    @property
    def allowed_roles_as_string(self) -> str:
        roles = ''
        guild = bot.instance.get_guild(self.guild_id)
        for role_id in self._allowed_roles:
            role = guild.get_role(role_id)
            roles = ', '.join([roles, role.mention])
        return roles.lstrip(', ')

    def get(self, user: int) -> GuildMissedRunRecord:
        for record in self._list:
            if record.user == user:
                return record
        return None

    def eligable(self, user: int):
        record = self.get(user)
        return not record is None and record.amount >= 3

    def member_allowed(self, member: Member) -> bool:
        for role in member.roles:
            if role.id in self._blacklisted_roles:
                return False
        for role in member.roles:
            if role.id in self._allowed_roles:
                return True
        return False

    def inc(self, user: int):
        db = bot.instance.data.db
        db.connect()
        try:
            record = self.get(user)
            if record:
                db.query(f'update missed_records set amount={record.amount + 1} where guild_id={self.guild_id} and user_id={user}')
            else:
                db.query(f'insert into missed_records (guild_id, user_id, amount) values ({self.guild_id}, {user}, {1})')
            self.load(self.guild_id)
        finally:
            db.disconnect()

    def remove(self, user: int):
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from missed_records where guild_id={self.guild_id} and user_id={user}')
            self.load(self.guild_id)
        finally:
            db.disconnect()
