from typing import List
from data.table.channels import ChannelData
from data.table.database import Database, DatabaseOperation
from data.table.guilds import GuildData
from data.table.schedule import ScheduleType

class RuntimeGuildData:
    _list: List[GuildData]
    
    def __init__(self) -> None:
        self._list = []
        
    def contains(self, guild: int) -> bool:
        return self.get_data(guild)
    
    def get_data(self, guild: int) -> GuildData:
        for data in self._list:
            if data.guild_id == guild:
                return data
        return None

    def init(self, db: Database, guild: int):
        self._list.append(GuildData(guild, 0, 0))
        db.connect()
        try:
            db.query(f'insert into guilds values ({str(guild)})')
        finally:
            db.disconnect()
        
    def load(self, db: Database):
        db.connect()
        try:
            gd = db.query('select guild_id, schedule_channel, schedule_post from guilds')
            for gd_record in gd:
                guild_data = GuildData(gd_record[0], gd_record[1], gd_record[2])
                cd = db.query(f'select type, channel_id from channels where guild_id={guild_data.guild_id}')
                for cd_record in cd:
                    guild_data.channels.append(ChannelData(guild_data.guild_id, cd_record[0], cd_record[1]))
                self._list.append(guild_data)
        finally:
            db.disconnect()
            
    def save_schedule_post(self, db: Database, guild: int, channel: int, post: int):
        db.connect()
        try:
            db.query(f'insert into guilds values ({str(guild)}, {str(channel)}, {str(post)})')
        finally:
            db.disconnect()
            
    def set_schedule_channel(self, db: Database, guild: int, type: ScheduleType, channel: int) -> DatabaseOperation:
        if not self.contains(guild):
            self.init(db, guild)
        
        self.get_data(guild).channels.append(ChannelData(guild, type, channel))
        db.connect()
        try:
            if db.query(f'select channel_id from channels where guild_id={guild} and type=\'{type}\''):
                db.query(f'update channels set channel_id={channel} where guild_id={guild} and type=\'{type}\'')
                return DatabaseOperation.EDITED
            else:
                db.query(f'insert into channels (guild_id, type, channel_id) values ({str(guild)}, \'{str(type)}\', {str(channel)})')
                return DatabaseOperation.ADDED
        finally:
            db.disconnect()
        