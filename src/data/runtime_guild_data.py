from typing import List
from data.table.channels import ChannelData
from data.table.database import Database, DatabaseOperation
from data.table.guilds import GuildData
from data.table.schedule import ScheduleType
import bot as rgd_bot

class RuntimeGuildData:
    """Runtime data object containing information on guild's 
    different registered channels.

    Properties
    ----------
    _list: :class:`List[GuildData]`
        List of all the different guild information.
    """
    _list: List[GuildData]
    
    def __init__(self) -> None:
        self._list = []
        
    def contains(self, guild: int) -> bool:
        """Does the guild information exist for the guild?

        Args:
            guild (int): guild id
        """
        return self.get_data(guild)
    
    def get_data(self, guild: int) -> GuildData:
        """Gets the guild information for the guild.

        Args:
            guild (int): guild id.
        """
        for data in self._list:
            if data.guild_id == guild:
                return data
        return None

    def init(self, db: Database, guild: int):
        """Initializes empty guild information object.

        Args:
            db (Database): please remove
            guild (int): guild id
        
        TODO:
            Remove db parameter.
        """
        self._list.append(GuildData(guild, 0, 0))
        db.connect()
        try:
            db.query(f'insert into guilds values ({str(guild)})')
        finally:
            db.disconnect()
        
    def load(self, db: Database):
        """Loads all the guild and channel information from the database.

        Args:
            db (Database): please remove
            
        TODO:
            Remove db parameter.
        """
        db.connect()
        try:
            gd = db.query('select guild_id, schedule_channel, schedule_post from guilds')
            for gd_record in gd:
                guild_data = GuildData(gd_record[0], gd_record[1], gd_record[2])
                cd = db.query(f'select type, channel_id, is_pl_channel, is_support_channel from channels where guild_id={guild_data.guild_id}')
                for cd_record in cd:
                    guild_data._channels.append(ChannelData(guild_data.guild_id, cd_record[0], cd_record[1], cd_record[2], cd_record[3]))
                self._list.append(guild_data)
        finally:
            db.disconnect()
            
    def save_schedule_post(self, db: Database, guild: int, channel: int, post: int):
        """Saves schedule post information to the database.

        Args:
            db (Database): please remove
            guild (int): guild id.
            channel (int): Schedule post's channel id.
            post (int): Schedule post's message id.
            
        TODO:
            Remove db parameter.
        """
        if not self.contains(guild):
            self.init(db, guild)
        self.get_data(guild).schedule_channel = channel
        self.get_data(guild).schedule_post = post    
        db.connect()
        try:
            db.query(f'update guilds set schedule_channel={str(channel)}, schedule_post={str(post)}')
        finally:
            db.disconnect()
            
    def set_schedule_channel(self, db: Database, guild: int, type: ScheduleType, channel: int) -> DatabaseOperation:
        """Sets the channel for the event type, where the passcodes are posted.

        Args:
            db (Database): please remove
            guild (int): guild id.
            type (ScheduleType): Event type
            channel (int): channel id for the event type

        Returns:
            DatabaseOperation: Was the channel changed or added?
            
        TODO:
            Remove db parameter.
        """
        if not self.contains(guild):
            self.init(db, guild)
            
        if type == ScheduleType.BA_ALL.value:
            self.set_schedule_channel(db, guild, ScheduleType.BA_NORMAL.value, channel)
            self.set_schedule_channel(db, guild, ScheduleType.BA_RECLEAR.value, channel)
            self.set_schedule_channel(db, guild, ScheduleType.BA_SPECIAL.value, channel)
            return
        
        self.get_data(guild).remove_channel(type=type)
        self.get_data(guild).add_channel(channel, type)
        db.connect()
        try:
            if db.query(f'select channel_id from channels where guild_id={guild} and type=\'{type}\' and not is_pl_channel and not is_support_channel'):
                db.query(f'update channels set channel_id={channel} where guild_id={guild} and type=\'{type}\' and not is_pl_channel and not is_support_channel')
                return DatabaseOperation.EDITED
            else:
                db.query(f'insert into channels (guild_id, type, channel_id) values ({str(guild)}, \'{str(type)}\', {str(channel)})')
                return DatabaseOperation.ADDED
        finally:
            db.disconnect()
    
    def set_party_leader_channel(self, db: Database, guild: int, type: ScheduleType, channel: int) -> DatabaseOperation:
        """Sets the channel for the event type, where the party leader recruitment posts are posted.

        Args:
            db (Database): please remove
            guild (int): guild id.
            type (ScheduleType): Event type
            channel (int): channel id for the event type

        Returns:
            DatabaseOperation: Was the channel changed or added?
            
        TODO:
            Remove db parameter.
        """
        if not self.contains(guild):
            self.init(db, guild)
            
        if type == ScheduleType.BA_ALL.value:
            self.set_party_leader_channel(db, guild, ScheduleType.BA_NORMAL.value, channel)
            self.set_party_leader_channel(db, guild, ScheduleType.BA_RECLEAR.value, channel)
            self.set_party_leader_channel(db, guild, ScheduleType.BA_SPECIAL.value, channel)
            return
        
        self.get_data(guild).remove_channel(type=type)
        self.get_data(guild).add_channel(channel, type, True)
        db.connect()
        try:
            if db.query(f'select channel_id from channels where guild_id={guild} and type=\'{type}\' and is_pl_channel'):
                db.query(f'update channels set channel_id={channel} where guild_id={guild} and type=\'{type}\' and is_pl_channel')
                return DatabaseOperation.EDITED
            else:
                db.query(f'insert into channels (guild_id, type, channel_id, is_pl_channel) values ({str(guild)}, \'{str(type)}\', {str(channel)}, true)')
                return DatabaseOperation.ADDED
        finally:
            db.disconnect()
            
    def set_schedule_support_channel(self, guild: int, type: ScheduleType, channel: int) -> DatabaseOperation:
        """Sets the channel for the event type, where the support passcodes are posted.

        Args:
            guild (int): guild id.
            type (ScheduleType): Event type
            channel (int): channel id for the event type

        Returns:
            DatabaseOperation: Was the channel changed or added?
        """
        if not self.contains(guild):
            self.init(rgd_bot.snowcaloid.data.db, guild)
        
        if type == ScheduleType.BA_ALL.value:
            self.set_schedule_support_channel(guild, ScheduleType.BA_NORMAL.value, channel)
            self.set_schedule_support_channel(guild, ScheduleType.BA_RECLEAR.value, channel)
            self.set_schedule_support_channel(guild, ScheduleType.BA_SPECIAL.value, channel)
            return DatabaseOperation.EDITED
        
        self.get_data(guild).remove_channel(type=type)
        self.get_data(guild).add_channel(channel, type, False, True)
        rgd_bot.snowcaloid.data.db.connect()
        try:
            if rgd_bot.snowcaloid.data.db.query(f'select channel_id from channels where guild_id={guild} and type=\'{type}\' and is_support_channel'):
                rgd_bot.snowcaloid.data.db.query(f'update channels set channel_id={channel} where guild_id={guild} and type=\'{type}\' and is_support_channel')
                return DatabaseOperation.EDITED
            else:
                rgd_bot.snowcaloid.data.db.query(f'insert into channels (guild_id, type, channel_id, is_support_channel) values ({str(guild)}, \'{str(type)}\', {str(channel)}, true)')
                return DatabaseOperation.ADDED
        finally:
            rgd_bot.snowcaloid.data.db.disconnect()
        