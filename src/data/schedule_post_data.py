from typing import List, Union
from data.runtime_guild_data import RuntimeGuildData
from data.table.database import Database, pg_timestamp
from data.table.schedule import ScheduleType, ScheduleData, schedule_type_desc
from datetime import datetime, date
from discord.ext.commands import Bot

class Error_Missing_Schedule_Post(Exception): pass
class Error_Cannot_Remove_Schedule(Exception): pass
class Error_Invalid_Schedule_Id(Exception): pass
class Error_Insufficient_Permissions(Exception): pass
class Error_Invalid_Date(Exception): pass

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
        
    def add_entry(self, db: Database, owner: int, type: ScheduleType, timestamp: datetime, description: str = '', auto_passcode: bool = True) -> Union[int, ScheduleData]:
        entry = ScheduleData(owner, type, timestamp, description)
        if auto_passcode and not type in [ScheduleType.BA_RECLEAR.value, ScheduleType.BA_SPECIAL.value]:
            entry.generate_passcode(type in [ScheduleType.BA_NORMAL.value])
        self._list.append(entry)        
        if db:
            db.connect()
            try:
                id = db.query(f'insert into schedule (schedule_post, owner, type, timestamp, description, pass_main, pass_supp) ' +
                              f'values ({self.post}, {owner}, \'{type}\', {pg_timestamp(timestamp)}, \'{description}\', {str(int(entry.pass_main))}, {str(int(entry.pass_supp))}) returning id')
                entry.id = id
                return id
            finally:
                db.disconnect()
        else:
            return entry
    
    def edit_entry(self, db: Database, id: int, owner: int, type: ScheduleType, date: datetime, time: datetime, description: str, passcode: bool, is_admin: bool) -> int:
        entry = self.get_entry(id)
        if entry:
            if owner == entry.owner or is_admin:
                set_str = ''
                if date or time:
                    old_timestamp = entry.timestamp
                    if date:
                        entry.timestamp = datetime(year=date.year, month=date.month, day=date.day, hour=entry.timestamp.hour, minute=entry.timestamp.minute)
                    if time:
                        entry.timestamp = datetime(year=entry.timestamp.year, month=entry.timestamp.month, day=entry.timestamp.day, hour=time.hour, minute=time.minute)
                    if entry.timestamp < datetime.now():
                        entry.timestamp = old_timestamp
                        raise Error_Invalid_Date()
                    set_str += f'timestamp={pg_timestamp(entry.timestamp)}'
                if passcode:
                    entry.generate_passcode(True)
                else:
                    entry.pass_main = 0
                    entry.pass_supp = 0
                if set_str:
                    set_str += f', pass_main={str(entry.pass_main)}, pass_supp={str(entry.pass_supp)} '
                else:
                    set_str += f'pass_main={str(entry.pass_main)}, pass_supp={str(entry.pass_supp)} '
                if owner:
                    entry.owner = owner
                    set_str += f', owner={str(owner)}'
                if type:
                    entry.type = type
                    set_str += f', type=\'{type}\''
                if description:
                    entry.description = description 
                    set_str += f', description=\'{description}\''      
                if db:
                    db.connect()
                    try:
                        db.query(f'update schedule set {set_str} where id={id}')
                    finally:
                        db.disconnect()
            else:
                raise Error_Insufficient_Permissions()
        else:
            raise Error_Invalid_Schedule_Id()
    
    async def remove_entry(self, db: Database, bot: Bot, owner: int, admin: bool, id: int):
        self.remove(id)
        db.connect()
        try:
            u = db.query(f'select owner from schedule where id={id}')[0][0]
            if u == owner or admin:
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
                                                                entry.timestamp.strftime("%H:%M") + f' CET: {schedule_type_desc(entry.type)} (Leader: {guild.get_member(entry.owner).name})'])
                                    if entry.description:
                                        schedule_on_day += f' [{entry.description}]'
                                embed.add_field(name=data.date.strftime("%A, %d %B %Y"), value=schedule_on_day.lstrip("\n"))
                                
                            await post.edit(embed=embed)
                        else:
                            raise Exception(f'Could not find message with ID {self.post}')
        
class SchedulePostData():
    _list: List[SchedulePost]
    guild_data: RuntimeGuildData
    
    def __init__(self, guild_data: RuntimeGuildData):
        self._list = []
        self.guild_data = guild_data
    
    def contains(self, guild: int) -> bool:
        return self.get_post(guild)
    
    def get_post(self, guild: int) -> SchedulePost:
        for entry in self._list:
            if entry.guild == guild:
                return entry
        return None
    
    def add_entry(self, db: Database, guild: int, owner: int, type: ScheduleType, timestamp: datetime, description: str = '') -> int:
        if self.contains(guild): 
            return self.get_post(guild).add_entry(db, owner, type, timestamp, description)
        else:
            raise Error_Missing_Schedule_Post() 
    
    def edit_entry(self, db: Database, id: int, guild: int, owner: int, type: ScheduleType, date: datetime, time: datetime, description: str, passcode: bool, is_admin: bool) -> int:
        if self.contains(guild): 
            return self.get_post(guild).edit_entry(db, id, owner, type, date, time, description, passcode, is_admin)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def remove_entry(self, db: Database, bot: Bot, guild: int, owner: int, admin: bool, id: int):
        if self.contains(guild):
            await self.get_post(guild).remove_entry(db, bot, owner, admin, id)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def update_post(self, guild: int, bot: Bot):
        if self.contains(guild): 
            await self.get_post(guild).update_post(bot)
        else:
            raise Error_Missing_Schedule_Post() 
    
    def save(self, db: Database, guild: int, channel: int, post: int):
        self._list.append(SchedulePost(guild, channel, post))
        self.guild_data.save_schedule_post(db, guild, channel, post)
            
    async def load(self, bot: Bot, db: Database):
        db.connect()
        try:
            self._list.clear()
            for guild_data in self.guild_data._list:
                schedule_post = SchedulePost(guild_data.guild_id, guild_data.schedule_channel, guild_data.schedule_post)
                for sch_record in db.query(f'select id, owner, type, timestamp, description from schedule where schedule_post={guild_data.schedule_post}'):
                    entry = schedule_post.add_entry(None, sch_record[1], sch_record[2], sch_record[3], sch_record[4])
                    entry.id = sch_record[0]
                self._list.append(schedule_post)
                await schedule_post.update_post(bot)
        finally:
            db.disconnect()