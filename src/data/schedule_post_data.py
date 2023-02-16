from typing import List, Union
from buttons import ButtonType, PartyLeaderButton
from data.runtime_guild_data import RuntimeGuildData
from data.table.database import Database, pg_timestamp
from data.table.guilds import GuildData
from data.table.schedule import ScheduleType, ScheduleData, schedule_type_desc
from datetime import datetime, date, timedelta
from discord import Embed, Message
import bot as schedule_post_data_bot
from data.table.tasks import TaskExecutionType

from utils import button_custom_id, unix_time
from views import PersistentView

class Error_Missing_Schedule_Post(Exception): pass
class Error_Cannot_Remove_Schedule(Exception): pass
class Error_Invalid_Schedule_Id(Exception): pass
class Error_Insufficient_Permissions(Exception): pass
class Error_Invalid_Date(Exception): pass

class DateSeparatedScheduleData:
    """Helper class for separating Schedule entries by date."""
    _list: List[ScheduleData]
    _date: date
    
    def __init__(self, date: date) -> None:
        self._date = date
        self._list = []

class SchedulePost:
    """Runtime data object containing information regarding Schedule 
    for a certain guild.
    
    Properties
    ----------
    guild: :class:`int`
        Guild ID.
    channel: :class:`int`
        Channel ID, where the schedule post is located.
    post: :class:`int`
        Message ID of the schedule post. This message should be placed 
        in a channel, which doesn't have more than 50 messages posted 
        simultaneously after the post.
    _list: :class:`List[ScheduleData]`
        List of all the scheduled events in the given guild.
    """
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
        """Does the event <id> exist in this guild?

        Args:
            id (int): event id
        """
        return self.get_entry(id)
    
    def get_entry(self, id: int) -> ScheduleData:
        """Get the event <id>.

        Args:
            id (int): event id
        """
        for data in self._list:
            if data.id == id:
                return data
        return None

    def get_entry_by_pl_post(self, post_id: int) -> ScheduleData:
        """Get the event by it's party leader post.

        Args:
            post_id (int): party leader message id
        """
        for data in self._list:
            if data.post_id == post_id:
                return data
        return None
    
    def remove(self, id: int):
        """Remove event from the runtime data and the database.

        Args:
            id (int): event id
        """
        for data in self._list:
            if data.id == id:
                self._list.remove(data)
                schedule_post_data_bot.snowcaloid.data.db.connect()
                try:
                    schedule_post_data_bot.snowcaloid.data.db.query(f'delete from schedule where id={id}')
                    schedule_post_data_bot.snowcaloid.data.db.query(f'delete from buttons where button_id ~ \'{data.post_id}\'')
                finally:
                    schedule_post_data_bot.snowcaloid.data.db.disconnect()
        
    def add_entry(self, db: Database, owner: int, type: ScheduleType, timestamp: datetime, description: str = '', auto_passcode: bool = True) -> Union[int, ScheduleData]:
        """Add an event to the guild's schedule.

        Args:
            owner (int): Event owner (user id). Typically the caller of /schedule_add
            type (ScheduleType): Type of event that is being scheduled.
            timestamp (datetime): When is the run taking place?
            description (str, optional): Description for the run. Defaults to ''.
            auto_passcode (bool, optional): Is the passcode automatically generated?. Defaults to True.

        Returns:
            Union[int, ScheduleData]: If called by runtime, it returns the id of the event. If called by loading from database, returns the event object. 
        TODO:
            Refactor database parameter. 
            Always return the event itself.
        """
        entry = ScheduleData(owner, type, timestamp, description)
        if auto_passcode and (not entry.pass_main or not entry.pass_supp):
            entry.generate_passcode(True)
        self._list.append(entry)       
        if db:
            db.connect()
            try:
                id = db.query(f'insert into schedule (schedule_post, owner, type, timestamp, description, pass_main, pass_supp) ' +
                              f'values ({self.post}, {owner}, \'{type}\', {pg_timestamp(timestamp)}, \'{description}\', {str(int(entry.pass_main))}, {str(int(entry.pass_supp))}) returning id')
                entry.id = id
                schedule_post_data_bot.snowcaloid.data.tasks.add_task(timestamp, TaskExecutionType.REMOVE_OLD_RUNS, {"id": id})
                schedule_post_data_bot.snowcaloid.data.tasks.add_task(timestamp - timedelta(hours=1), TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild, "entry_id": id}) 
                if auto_passcode:
                    schedule_post_data_bot.snowcaloid.data.tasks.add_task(timestamp - timedelta(minutes=35), TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild, "entry_id": id}) 
                    schedule_post_data_bot.snowcaloid.data.tasks.add_task(timestamp - timedelta(minutes=30), TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild, "entry_id": id}) 
                return id
            finally:
                db.disconnect()
        else:
            return entry
    
    def edit_entry(self, db: Database, id: int, owner: int, type: ScheduleType, date: datetime, time: datetime, description: str, passcode: bool, is_admin: bool):
        """Edits the event.

        Args:
            id (int): event id.
            owner (int): User ID of the user trying to edit the entry.
            type (ScheduleType): Event type
            date (datetime): Date of the event
            time (datetime): Time of the event
            description (str): Description of the event
            passcode (bool): Is the passcode needed?
            is_admin (bool): Does the calling user have admin rights / rights to edit other's runs?

        Raises:
            Error_Invalid_Date: Date is invalid
            Error_Insufficient_Permissions: The user doesn't have permissions to change the event.
            Error_Invalid_Schedule_Id: The schedule id is invalid.

        TODO:
            Refactor the db parameter.
            Rename owner parameter.
        """
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
                    entry.timestamp = entry.timestamp.timestamp()
                    if entry.timestamp < datetime.utcnow():
                        entry.timestamp = old_timestamp
                        raise Error_Invalid_Date()
                    set_str += f'timestamp={pg_timestamp(entry.timestamp)}'
                if passcode and (not entry.pass_main or not entry.pass_supp):
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
        """Remove the event <id>.

        Args:
            owner (int): User ID of the user trying to edit the entry.
            admin (bool): Does the calling user have admin rights / rights to edit other's runs?
            id (int): event id

        Raises:
            Error_Cannot_Remove_Schedule: The user doesn't have permissions to change the event.
        
        TODO:
            Remove the db parameter.
            Rename owner parameter.
        """
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
        """Splits the event list by date."""
        result = []
        entry = None
        for data in self._list:
            if not entry or entry._date != data.timestamp.date():
                entry = DateSeparatedScheduleData(data.timestamp.date())
                result.append(entry)
            entry._list.append(data)
                
        return result
                
    async def update_post(self): 
        """Updates the schedule post."""
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
        """Updates the party leader recruitment post.

        Args:
            guild_data (GuildData): Runtime guild data object for the current guild
            entry (ScheduleData, optional): Event, whose post will be updated. Defaults to 
                None - not needed if `id` or `post_id` are supplied.
            message (Message, optional): Message, that will be edited. Defaults to None - 
                then tries to find it using event data.
            post_id (int, optional): Message ID of the party leader post. Defaults to 0 - 
                not needed if `entry` or `id` are supplied.
            id (int, optional): Event id. Defaults to 0 - not needed if `event` or `post_id` 
                are supplied.

        TODO:  
            Remove guild_data parameter and get it automatically.
        """
        if not entry:
            if post_id:
                entry = self.get_entry_by_pl_post(post_id)
            elif id:
                entry = self.get_entry(id)
            else:
                raise Exception('missing entry in update_pl_post')
        if not message:
            pl_channel = guild_data.get_pl_channel(entry.type)
            if pl_channel:
                channel = await schedule_post_data_bot.snowcaloid.get_guild(self.guild).fetch_channel(pl_channel.channel_id)
                message = await channel.fetch_message(entry.post_id)
        if message:
            embed = Embed(title=entry.timestamp.strftime('%A, %d %B %Y %H:%M ') + schedule_type_desc(entry.type) + "\nParty leader recruitment")
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
        """Create the party leader post for event <id>

        Args:
            id (int): event id.
            guild_data (GuildData): Runtime guild data for the guild.
        
        TODO:
            Remove guild_data parameter and get it automatically.
        """
        entry = self.get_entry(id)
        pl_channel = guild_data.get_pl_channel(entry.type)
        if pl_channel:
            channel = await schedule_post_data_bot.snowcaloid.get_guild(self.guild).fetch_channel(pl_channel.channel_id)
            message = await channel.send(f'Recruitment post #{str(id)}')
            entry.post_id = message.id
            view = PersistentView()
            for i in range(1, 7):    
                button = PartyLeaderButton(label=str(i), custom_id=button_custom_id(f'pl{i}', message, ButtonType.PL_POST), row=1 if i < 4 else 2)
                view.add_item(button)
            view.add_item(PartyLeaderButton(label='Support', custom_id=button_custom_id('pl7', message, ButtonType.PL_POST), row=2))
            await self.update_pl_post(guild_data, entry=entry, message=message)
            await message.edit(view=view)
            schedule_post_data_bot.snowcaloid.data.tasks.add_task(entry.timestamp + timedelta(hours=12), TaskExecutionType.REMOVE_OLD_PL_POSTS, {"guild": self.guild, "channel": channel.id})
            schedule_post_data_bot.snowcaloid.data.db.connect()
            try:
                schedule_post_data_bot.snowcaloid.data.db.query(f'update schedule set post_id={entry.post_id} where id={id}')
                for button in view.children:
                    schedule_post_data_bot.snowcaloid.data.db.query(f'insert into buttons values (\'{button.custom_id}\', \'{button.label}\')')
            finally:
                schedule_post_data_bot.snowcaloid.data.db.disconnect()
        else: 
            print(f'Info: no party leader post has been made due to the missing channel for type {type} in guild {schedule_post_data_bot.snowcaloid.get_guild(self.guild).name}')
            
        
class SchedulePostData():
    """Runtime data object containing all schedule information for all guilds.
    
    Properties
    ----------
    _list: :class:`List[SchedulePost]`
        List of all schedule information, seperated by guild.
    guild_data: :class:`RuntimeGuildData`
        Runtime data which stores base properties of a guild, e.g which event type 
        should be posted in which channel.

    TODO:
        Remove guild_data and use global snowcaloid.data.guild_data.
    """
    _list: List[SchedulePost]
    guild_data: RuntimeGuildData
    
    def __init__(self, guild_data: RuntimeGuildData):
        self._list = []
        self.guild_data = guild_data
    
    def contains(self, guild: int) -> bool:
        """Does the guild contain a schedule post?

        Args:
            guild (int): guild id
        """
        return self.get_post(guild)
    
    def get_post(self, guild: int) -> SchedulePost:
        """Get the schedule post data for the guild.

        Args:
            guild (int): guild
        """
        for entry in self._list:
            if entry.guild == guild:
                return entry
        return None
    
    def add_entry(self, db: Database, guild: int, owner: int, type: ScheduleType, timestamp: datetime, description: str = '') -> int:
        """Add an event to the guild's schedule.

        Args:
            guild (int): guild id for the schedule post
            owner (int): Event owner (user id). Typically the caller of /schedule_add
            type (ScheduleType): Type of event that is being scheduled.
            timestamp (datetime): When is the run taking place?
            description (str, optional): Description for the run. Defaults to ''.
            
        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.

        Returns:
            Union[int, ScheduleData]: If called by runtime, it returns the id of the event. If called by loading from database, returns the event object. 
        
        TODO:
            Refactor the db parameter.
            Rename owner parameter.
        """
        if self.contains(guild): 
            return self.get_post(guild).add_entry(db, owner, type, timestamp, description)
        else:
            raise Error_Missing_Schedule_Post() 
    
    def edit_entry(self, db: Database, id: int, guild: int, owner: int, type: ScheduleType, date: datetime, time: datetime, description: str, passcode: bool, is_admin: bool) -> int:
        """Edits the event.

        Args:
            id (int): event id.
            guild (int): guild id for the schedule post
            owner (int): User ID of the user trying to edit the entry.
            type (ScheduleType): Event type
            date (datetime): Date of the event
            time (datetime): Time of the event
            description (str): Description of the event
            passcode (bool): Is the passcode needed?
            is_admin (bool): Does the calling user have admin rights / rights to edit other's runs?

        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.

        TODO:
            Refactor the db parameter.
            Rename owner parameter.
        """
        if self.contains(guild): 
            return self.get_post(guild).edit_entry(db, id, owner, type, date, time, description, passcode, is_admin)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def remove_entry(self, db: Database, guild: int, owner: int, admin: bool, id: int):
        """Remove the event <id>.

        Args:
            guild (int): guild id for the schedule post
            owner (int): User ID of the user trying to edit the entry.
            admin (bool): Does the calling user have admin rights / rights to edit other's runs?
            id (int): event id

        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.
        
        TODO:
            Remove the db parameter.
            Rename owner parameter.
        """
        if self.contains(guild):
            await self.get_post(guild).remove_entry(db, owner, admin, id)
        else:
            raise Error_Missing_Schedule_Post() 
        
    async def update_post(self, guild: int):
        """Updates the schedule post for guild.

        Args:
            guild (int): guild id.

        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.
        """
        if self.contains(guild): 
            await self.get_post(guild).update_post()
        else:
            raise Error_Missing_Schedule_Post() 
    
    async def create_pl_post(self, guild: int, id: int):
        """Create the party leader post for event <id> in guild <guild>.

        Args:
            guild (int): guild id.
            id (int): event id.
        """
        if self.contains(guild): 
            await self.get_post(guild).create_pl_post(id, self.guild_data.get_data(guild))
        else:
            raise Error_Missing_Schedule_Post() 
    
    def save(self, db: Database, guild: int, channel: int, post: int):
        """Saves the schedule post to the runtime object and the database.

        Args:
            db (Database): please remove this
            guild (int): guild id.
            channel (int): Schedule post channel id. 
            post (int): Schedule post message id.
            
        TODO:
            Remove db parameter.
        """
        self._list.append(SchedulePost(guild, channel, post))
        self.guild_data.save_schedule_post(db, guild, channel, post)
            
    async def load(self, db: Database):
        """Loads all schedule posts and events from the database.

        Args:
            db (Database): please remove this.
        
        TODO:
            Remove db parameter.
        """
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