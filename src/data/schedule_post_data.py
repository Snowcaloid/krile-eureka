from typing import List, Union
from buttons import ButtonType, PartyLeaderButton
from data.runtime_guild_data import RuntimeGuildData
from data.table.database import Database, pg_timestamp
from data.table.guilds import GuildData
from data.table.schedule import ScheduleType, ScheduleData, schedule_type_desc
from datetime import datetime, date
from discord import Embed, Message
import bot as schedule_post_data_bot

from utils import button_custom_id, unix_time
from views import PersistentView

class Error_Missing_Schedule_Post(Exception): pass
class Error_Cannot_Remove_Schedule(Exception): pass
class Error_Invalid_Schedule_Id(Exception): pass
class Error_Insufficient_Permissions(Exception): pass
class Error_Invalid_Date(Exception): pass

class DateSeparatedScheduleData:
    _list: List[ScheduleData]
    _date: date
    
    def __init__(self, date: date) -> None:
        self._date = date
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

    def get_entry_by_post(self, post_id: int) -> ScheduleData:
        for data in self._list:
            if data.post_id == post_id:
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
    
    async def remove_entry(self, db: Database, owner: int, admin: bool, id: int):
        self.remove(id)
        db.connect()
        try:
            u = db.query(f'select owner from schedule where id={id}')[0][0]
            if u == owner or admin:
                db.query(f'delete from schedule where id={id}')
                await self.update_post()
            else:
                raise Error_Cannot_Remove_Schedule()
        finally:
            db.disconnect()
                
    def split_per_date(self) -> List[DateSeparatedScheduleData]:
        result = []
        entry = None
        for data in self._list:
            if not entry or entry._date != data.timestamp.date():
                entry = DateSeparatedScheduleData(data.timestamp.date())
                result.append(entry)
            entry._list.append(data)
                
        return result
                
    async def update_post(self): 
        guild = schedule_post_data_bot.snowcaloid.get_guild(self.guild)       
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
                                                        entry.timestamp.strftime("%H:%M") + f' ST ({unix_time(entry.timestamp)} LT): {schedule_type_desc(entry.type)} (Leader: {guild.get_member(entry.owner).name})'])
                            if entry.description:
                                schedule_on_day += f' [{entry.description}]'
                        embed.add_field(name=data._date.strftime("%A, %d %B %Y"), value=schedule_on_day.lstrip("\n"))
                        
                    await post.edit(embed=embed)
                else:
                    raise Exception(f'Could not find message with ID {self.post}')
                
    async def update_pl_post(self, guild_data: GuildData, entry: ScheduleData = None, message: Message = None, post_id: int = 0, id: int = 0):
        if not entry:
            if post_id:
                entry = self.get_entry_by_post(post_id)
            elif id:
                entry = self.get_entry(id)
            else:
                raise Exception('missing entry in update_pl_post')
        if not message:
            pl_channel = guild_data.get_pl_channel(entry.type)
            if pl_channel:
                channel = await schedule_post_data_bot.snowcaloid.get_guild(guild_data.guild_id).fetch_channel(pl_channel.channel_id)
                message = await channel.fetch_message(entry.post_id)
        if message:
            embed = Embed(title=entry.timestamp.strftime('%A, %d %B %Y ') + schedule_type_desc(entry.type) + "\nParty leader recruitment")
            async def name(id: int) -> str: 
                if id:
                    return (await message.guild.fetch_member(id)).display_name
                else:
                    return ''
            embed.description = (
                f'Raid Leader: {await name(entry.owner)}\n'
                f'Party 1: {await name(entry.party_leaders[0])}\n'
                f'Party 2: {await name(entry.party_leaders[1])}\n'
                f'Party 3: {await name(entry.party_leaders[2])}\n'
                f'Party 4: {await name(entry.party_leaders[3])}\n'
                f'Party 5: {await name(entry.party_leaders[4])}\n'
                f'Party 6: {await name(entry.party_leaders[5])}\n'
                f'Support: {await name(entry.party_leaders[6])}\n\n'
                '*Use the button to volunteer to host a party.\n'
                'Please note, your entry may be removed at the Raid Leader\'s discretion.*'
            )
            await message.edit(embed=embed)
            
    
    async def create_pl_post(self, id: int, guild_data: GuildData):
        entry = self.get_entry(id)
        pl_channel = guild_data.get_pl_channel(entry.type)
        if pl_channel:
            channel = await schedule_post_data_bot.snowcaloid.get_guild(guild_data.guild_id).fetch_channel(pl_channel.channel_id)
            message = await channel.send(f'Recruitment post #{str(id)}')
            entry.post_id = message.id
            view = PersistentView()
            for i in range(1, 7):    
                button = PartyLeaderButton(label=str(i), custom_id=button_custom_id(f'pl{i}', message, ButtonType.PL_POST), row=1 if i < 4 else 2)
                view.add_item(button)
            view.add_item(PartyLeaderButton(label='Support', custom_id=button_custom_id('pl7', message, ButtonType.PL_POST)), row=2)
            await self.update_pl_post(guild_data, entry=entry, message=message)
            await message.edit(view=view)
            schedule_post_data_bot.snowcaloid.data.db.connect()
            try:
                schedule_post_data_bot.snowcaloid.data.db.query(f'update schedule set post_id={entry.post_id} where id={id}')
                for button in view.children:
                    schedule_post_data_bot.snowcaloid.data.db.query(f'insert into buttons values (\'{button.custom_id}\', \'{button.label}\')')
            finally:
                schedule_post_data_bot.snowcaloid.data.db.disconnect()
        else: 
            print(f'Info: no party leader post has been made due to the missing channel for type {type} in guild {schedule_post_data_bot.snowcaloid.get_guild(guild_data.guild_id).name}')
            
        
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
        
    async def remove_entry(self, db: Database, guild: int, owner: int, admin: bool, id: int):
        if self.contains(guild):
            await self.get_post(guild).remove_entry(db, owner, admin, id)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def update_post(self, guild: int):
        if self.contains(guild): 
            await self.get_post(guild).update_post()
        else:
            raise Error_Missing_Schedule_Post() 
    
    async def create_pl_post(self, guild: int, id: int):
        if self.contains(guild): 
            await self.get_post(guild).create_pl_post(id, self.guild_data.get_data(guild))
        else:
            raise Error_Missing_Schedule_Post() 
    
    def save(self, db: Database, guild: int, channel: int, post: int):
        self._list.append(SchedulePost(guild, channel, post))
        self.guild_data.save_schedule_post(db, guild, channel, post)
            
    async def load(self, db: Database):
        db.connect()
        try:
            self._list.clear()
            for guild_data in self.guild_data._list:
                schedule_post = SchedulePost(guild_data.guild_id, guild_data.schedule_channel, guild_data.schedule_post)
                for sch_record in db.query(f'select id, owner, type, timestamp, description, post_id, pl1, pl2, pl3, pl4, pl5, pl6, pls, pass_main, pass_supp from schedule where schedule_post={guild_data.schedule_post}'):
                    entry = schedule_post.add_entry(None, sch_record[1], sch_record[2], sch_record[3], sch_record[4])
                    entry.id = sch_record[0]
                    entry.post_id = sch_record[5]
                    entry.party_leaders = [sch_record[6], sch_record[7], sch_record[8], sch_record[9], sch_record[10], sch_record[11], sch_record[12]]
                    entry.pass_main = sch_record[13]
                    entry.pass_supp = sch_record[14]
                self._list.append(schedule_post)
                await schedule_post.update_post()
        finally:
            db.disconnect()