from typing import List
from data.table.channels import ChannelData
from data.table.database import Database, DatabaseOperation
from data.table.guilds import GuildData
from data.table.schedule import ScheduleType
import bot

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
        for data in self._list:
            if data.guild_id == guild:
                return True
        return False

    def get_data(self, guild: int) -> GuildData:
        """Gets the guild information for the guild.

        Args:
            guild (int): guild id.
        """
        if not self.contains(guild):
            self.init(guild)
        for data in self._list:
            if data.guild_id == guild:
                return data

    def init(self, guild: int):
        """Initializes empty guild information object.

        Args:
            guild (int): guild id
        """
        db = bot.snowcaloid.data.db
        db.connect()
        try:
            db.query(f'insert into guilds values ({str(guild)})')
        finally:
            db.disconnect()
        self._list.append(GuildData(guild, 0, 0, 0, 0, 0))

    def load(self):
        """Loads all the guild and channel information from the database."""
        db = bot.snowcaloid.data.db
        db.connect()
        try:
            gd = db.query('select guild_id, schedule_channel, schedule_post, missed_channel, missed_post, log_channel, missed_role from guilds')
            for gd_record in gd:
                guild_data = GuildData(gd_record[0], gd_record[1], gd_record[2], gd_record[3], gd_record[4], gd_record[5], gd_record[6])
                cd = db.query(f'select type, channel_id, is_pl_channel, is_support_channel from channels where guild_id={guild_data.guild_id}')
                for cd_record in cd:
                    guild_data._channels.append(ChannelData(guild_data.guild_id, cd_record[0], cd_record[1], cd_record[2], cd_record[3]))
                self._list.append(guild_data)
        finally:
            db.disconnect()

    def save_schedule_post(self, guild: int, channel: int, post: int):
        """Saves schedule post information to the database.

        Args:
            guild (int): guild id.
            channel (int): Schedule post's channel id.
            post (int): Schedule post's message id.
        """
        db = bot.snowcaloid.data.db
        db.connect()
        try:
            db.query(f'update guilds set schedule_channel={str(channel)}, schedule_post={str(post)} where guild_id={guild}')
        finally:
            db.disconnect()
        if not self.contains(guild):
            self.init(guild)
        self.get_data(guild).schedule_channel = channel
        self.get_data(guild).schedule_post = post

    def save_missed_runs_post(self, guild: int, channel: int, post: int):
        """Saves missed runs post information to the database.

        Args:
            guild (int): guild id.
            channel (int): Missed runs post's channel id.
            post (int): Missed runs post's message id.
        """
        db = bot.snowcaloid.data.db
        if not self.contains(guild):
            self.init(guild)
        self.get_data(guild).missed_channel = channel
        self.get_data(guild).missed_post = post
        db.connect()
        try:
            db.query(f'update guilds set missed_channel={str(channel)}, missed_post={str(post)}')
        finally:
            db.disconnect()

    def set_schedule_channel(self, guild: int, type: ScheduleType, channel: int) -> DatabaseOperation:
        """Sets the channel for the event type, where the passcodes are posted.

        Args:
            guild (int): guild id.
            type (ScheduleType): Event type
            channel (int): channel id for the event type

        Returns:
            DatabaseOperation: Was the channel changed or added?
        """
        if not self.contains(guild):
            self.init(guild)

        if type == ScheduleType.BA_ALL.value:
            self.set_schedule_channel(guild, ScheduleType.BA_NORMAL.value, channel)
            self.set_schedule_channel(guild, ScheduleType.BA_RECLEAR.value, channel)
            self.set_schedule_channel(guild, ScheduleType.BA_SPECIAL.value, channel)
            return

        self.get_data(guild).remove_channel(type=type)
        self.get_data(guild).add_channel(channel, type)
        db = bot.snowcaloid.data.db
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

    def set_party_leader_channel(self, guild: int, type: ScheduleType, channel: int) -> DatabaseOperation:
        """Sets the channel for the event type, where the party leader recruitment posts are posted.

        Args:
            guild (int): guild id.
            type (ScheduleType): Event type
            channel (int): channel id for the event type

        Returns:
            DatabaseOperation: Was the channel changed or added?
        """
        if not self.contains(guild):
            self.init(guild)

        if type == ScheduleType.BA_ALL.value:
            self.set_party_leader_channel(guild, ScheduleType.BA_NORMAL.value, channel)
            self.set_party_leader_channel(guild, ScheduleType.BA_RECLEAR.value, channel)
            self.set_party_leader_channel(guild, ScheduleType.BA_SPECIAL.value, channel)
            return

        self.get_data(guild).remove_channel(type=type)
        self.get_data(guild).add_channel(channel, type, True)
        db = bot.snowcaloid.data.db
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
            self.init(guild)

        if type == ScheduleType.BA_ALL.value:
            self.set_schedule_support_channel(guild, ScheduleType.BA_NORMAL.value, channel)
            self.set_schedule_support_channel(guild, ScheduleType.BA_RECLEAR.value, channel)
            self.set_schedule_support_channel(guild, ScheduleType.BA_SPECIAL.value, channel)
            return DatabaseOperation.EDITED

        self.get_data(guild).remove_channel(type=type)
        self.get_data(guild).add_channel(channel, type, False, True)
        bot.snowcaloid.data.db.connect()
        try:
            if bot.snowcaloid.data.db.query(f'select channel_id from channels where guild_id={guild} and type=\'{type}\' and is_support_channel'):
                bot.snowcaloid.data.db.query(f'update channels set channel_id={channel} where guild_id={guild} and type=\'{type}\' and is_support_channel')
                return DatabaseOperation.EDITED
            else:
                bot.snowcaloid.data.db.query(f'insert into channels (guild_id, type, channel_id, is_support_channel) values ({str(guild)}, \'{str(type)}\', {str(channel)}, true)')
                return DatabaseOperation.ADDED
        finally:
            bot.snowcaloid.data.db.disconnect()

    def set_log_channel(self, guild_id: int, new_channel_id: int) -> DatabaseOperation:
        """Changes the logging channel for the provided guild.

        Args:
            guild_id (int): the id of the guild to update
            new_channel_id (int): the new logging channel id

        Returns:
            DatabaseOperation: The outcome of the operation.
        """
        db = bot.snowcaloid.data.db

        if not self.contains(guild_id):
            self.init(guild_id)

        guild_data = self.get_data(guild_id)

        db.connect()
        try:
            if new_channel_id is None:
                # Remove the log channel id from the database and in-memory representation.
                db.query(f'UPDATE guilds SET log_channel = NULL WHERE guild_id = {guild_id}')
                guild_data.log_channel = None
                return DatabaseOperation.EDITED

            if guild_data.log_channel == new_channel_id:
                # We do not need to bother the database with this one.
                return DatabaseOperation.NONE

            if guild_data.log_channel is None:
                # The guild doesn't have a logging channel yet.
                operation = DatabaseOperation.ADDED
            else:
                # The user is changing the channel we are logging to.
                operation = DatabaseOperation.EDITED

            db.query(f'UPDATE guilds SET log_channel = {new_channel_id} WHERE guild_id = {guild_id}')

            # Update the value in-memory or the change will not apply until the bot restarts.
            guild_data.log_channel = new_channel_id

            return operation
        finally:
            db.disconnect()
