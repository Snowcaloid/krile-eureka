from typing import List
from data.table.database import Database, pg_timestamp
from data.table.schedule import ScheduleType, ScheduleData, schedule_type_desc
from datetime import datetime, date
from discord.ext.commands import Bot

class Error_Missing_Schedule_Post(Exception):
    pass

class Error_Cannot_Remove_Schedule(Exception):
    pass

class DateSeparatedScheduleData:
    _list: List[ScheduleData]
    date: date
    
    def __init__(self, date: date) -> None:
        self.date = date
        self._list = []

class SchedulePost:
    guild: int
    channel: int
    post: int
    _list: List[ScheduleData]
    
    def __init__(self, guild: int, channel: int, post: int):
        self.guild = guild
        self.channel = channel
        self.post = post
        self._list = []
    
    def contains(self, id: int) -> bool:
        return self.get_entry(id)
    
    def get_entry(self, id: int) -> ScheduleData:
        for data in self._list:
            if data.id == id:
                return data
        return None
    
    def remove(self, id: int):
        for data in self._list:
            if data.id == id:
                self._list.remove(data)
        
    def add_entry(self, db: Database, user: int, type: ScheduleType, timestamp: datetime, description: str = '') -> int:
        entry = ScheduleData(user, type, timestamp, description)
        self._list.append(entry)        
        if db:
            db.connect()
            try:
                id = db.query(f'insert into schedule (schedule_post, user_id, type, timestamp, description) values ({self.post}, {user}, \'{type}\', {pg_timestamp(timestamp)}, \'{description}\') returning id')
                entry.id = id
                return id
            finally:
                db.disconnect()
    
    async def remove_entry(self, db: Database, bot: Bot, user: int, admin: bool, id: int):
        self.remove(id)
        db.connect()
        try:
            u = db.query(f'select user from schedule where id={id}')[0][0]
            if u == user or admin:
                db.query(f'delete from schedule where id={id}')
                await self.update_post(bot)
            else:
                raise Error_Cannot_Remove_Schedule()
        finally:
            db.disconnect()
                
    def split_per_date(self) -> List[DateSeparatedScheduleData]:
        result = []
        entry = None
        for data in self._list:
            if not entry or entry.date != data.timestamp.date():
                entry = DateSeparatedScheduleData(data.timestamp.date())
                result.append(entry)
            entry._list.append(data)
                
        return result
                
    async def update_post(self, bot: Bot):        
        for guild in bot.guilds:
            if guild.id == self.guild:
                for channel in await guild.fetch_channels():
                    if channel.id == self.channel:
                        post = await channel.fetch_message(self.post)
                        if post:
                            embed = post.embeds[0]
                            embed.clear_fields()
                            self._list.sort(key=lambda d: d.timestamp)
                            per_date = self.split_per_date()
                            for data in per_date:
                                schedule_on_day = ''
                                for entry in data._list:
                                    schedule_on_day = "\n".join([schedule_on_day,
                                                                entry.timestamp.strftime("%H:%M") + f' CET: {schedule_type_desc(entry.type)} (Leader: {guild.get_member(entry.user).name})'])
                                    if entry.description:
                                        schedule_on_day += f' [{entry.description}]'
                                embed.add_field(name=data.date.strftime("%A, %d %B %Y"), value=schedule_on_day.lstrip("\n"))
                                
                            await post.edit(embed=embed)
                        else:
                            raise Exception(f'Could not find message with ID {self.post}')
        
class SchedulePostData():
    _list: List[SchedulePost] = []
    
    def contains(self, guild: int) -> bool:
        return self.get_post(guild)
    
    def get_post(self, guild: int) -> SchedulePost:
        for entry in self._list:
            if entry.guild == guild:
                return entry
        return None
    
    def add_entry(self, db: Database, guild: int, user: int, type: ScheduleType, timestamp: datetime, description: str = '') -> int:
        if self.contains(guild): 
            return self.get_post(guild).add_entry(db, user, type, timestamp, description)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def remove_entry(self, db: Database, bot: Bot, guild: int, user: int, admin: bool, id: int):
        if self.contains(guild):
            await self.get_post(guild).remove_entry(db, bot, user, admin, id)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def update_post(self, guild: int, bot: Bot):
        if self.contains(guild): 
            await self.get_post(guild).update_post(bot)
        else:
            raise Error_Missing_Schedule_Post() 
    
    def save(self, db: Database, guild: int, channel: int, post: int):
        db.connect()
        try:
            self._list.append(SchedulePost(guild, channel, post))
            db.query(f'insert into guilds values ({str(guild)}, {str(channel)}, {str(post)})')
        finally:
            db.disconnect()
            
    async def load(self, bot: Bot, db: Database):
        db.connect()
        try:
            self._list.clear()
            for gld_record in db.query('select guild_id, schedule_channel, schedule_post from guilds'):
                schedule_post = SchedulePost(gld_record[0], gld_record[1], gld_record[2])
                for sch_record in db.query(f'select id, user_id, type, timestamp, description from schedule where schedule_post={gld_record[2]}'):
                    schedule_post.add_entry(None, sch_record[1], sch_record[2], sch_record[3], sch_record[4])
                    schedule_post.id = sch_record[0]
                    
                self._list.append(schedule_post)
                await schedule_post.update_post(bot)
        finally:
            db.disconnect()