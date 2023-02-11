from typing import List
from data.table.database import Database

class SchedulePostData():
    class SchedulePostEntry:
        guild: int
        channel: int
        post: int
        
        def __init__(self, guild: int, channel: int, post: int):
            self.guild = guild
            self.channel = channel
            self.post = post
        
    _list: List[SchedulePostEntry] = []
    
    def contains(self, guild: int) -> bool:
        for entry in self._list:
            if entry.guild == guild:
                return True
        return False
    
    def save(self, db: Database, guild: int, channel: int, post: int):
        db.connect()
        try:
            self._list.append(SchedulePostData.SchedulePostEntry(guild, channel, post))
            db.query(f'insert into guilds values ({str(guild)}, {str(channel)}, {str(post)})')
        finally:
            db.disconnect()
            
    def load(self, db: Database):
        db.connect()
        try:
            self._list.clear()
            for record in db.query('select guild_id, schedule_channel, schedule_post from guilds'):
                self._list.append(SchedulePostData.SchedulePostEntry(record[0], record[1], record[2]))
        finally:
            db.disconnect()