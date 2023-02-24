import bot
import data.message_cache as cache
from typing import List
from buttons import ButtonType, PartyLeaderButton
from data.runtime_guild_data import RuntimeGuildData
from data.table.database import pg_timestamp
from data.table.guilds import GuildData
from data.table.schedule import ScheduleType, ScheduleData, schedule_type_desc
from datetime import datetime, date, timedelta
from discord import Embed, Message, TextChannel
from data.table.tasks import TaskExecutionType

from utils import button_custom_id, get_mention, set_default_footer, get_discord_timestamp
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
                bot.snowcaloid.data.db.connect()
                try:
                    bot.snowcaloid.data.db.query(f'delete from schedule where id={id}')
                    bot.snowcaloid.data.db.query(f'delete from buttons where button_id ~ \'{data.post_id}\'')
                finally:
                    bot.snowcaloid.data.db.disconnect()

    def add_entry(self, leader: int, type: ScheduleType, timestamp: datetime, description: str = '', auto_passcode: bool = True) -> ScheduleData:
        """Add an event to the guild's schedule.

        Args:
            leader (int): Event leader (user id). Typically the caller of /schedule_add
            type (ScheduleType): Type of event that is being scheduled.
            timestamp (datetime): When is the run taking place?
            description (str, optional): Description for the run. Defaults to ''.
            auto_passcode (bool, optional): Is the passcode automatically generated?. Defaults to True.

        Returns:
            ScheduleData: the event object.
        """
        entry = ScheduleData(leader, type, timestamp, description)
        if auto_passcode and (not entry.pass_main or not entry.pass_supp):
            entry.generate_passcode(True)
        self._list.append(entry)
        db = bot.snowcaloid.data.db
        if not db.connected():
            db.connect()
            try:
                id = db.query((
                    'insert into schedule (schedule_post, leader, type, timestamp, description, pass_main, pass_supp) '
                    f'values ({self.post}, {entry.leader}, \'{entry.type}\', {pg_timestamp(entry.timestamp)}, '
                    f'\'{entry.description}\', {str(int(entry.pass_main))}, {str(int(entry.pass_supp))}) returning id'
                ))
                entry.id = id
                bot.snowcaloid.data.tasks.add_task(timestamp, TaskExecutionType.REMOVE_OLD_RUNS, {"id": id})
                if auto_passcode:
                    bot.snowcaloid.data.tasks.add_task(timestamp - timedelta(hours=1), TaskExecutionType.SEND_PL_PASSCODES, {"guild": self.guild, "entry_id": id})
                    bot.snowcaloid.data.tasks.add_task(timestamp - timedelta(minutes=35), TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild, "entry_id": id})
                    bot.snowcaloid.data.tasks.add_task(timestamp - timedelta(minutes=30), TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild, "entry_id": id})
            finally:
                db.disconnect()
        return entry

    def edit_entry(self, id: int, leader: int, type: ScheduleType, date: datetime, time: datetime, description: str, passcode: bool, is_admin: bool):
        """Edits the event.

        Args:
            id (int): event id.
            leader (int): User ID of the user trying to edit the entry.
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
        """
        entry = self.get_entry(id)
        if entry:
            if leader == entry.leader or is_admin:
                set_str = ''
                if date or time:
                    old_timestamp = entry.timestamp
                    if date:
                        entry.timestamp = datetime(year=date.year, month=date.month, day=date.day, hour=entry.timestamp.hour, minute=entry.timestamp.minute)
                    if time:
                        entry.timestamp = datetime(year=entry.timestamp.year, month=entry.timestamp.month, day=entry.timestamp.day, hour=time.hour, minute=time.minute)
                    if entry.timestamp < datetime.utcnow():
                        entry.timestamp = old_timestamp
                        raise Error_Invalid_Date()
                    set_str += f'timestamp={pg_timestamp(entry.timestamp)}'
                if passcode and (not entry.pass_main or not entry.pass_supp):
                    entry.generate_passcode(True)
                    guild_data = bot.snowcaloid.data.guild_data.get_data(self.guild)
                    if guild_data:
                        channel_data = guild_data.get_channel(type=entry.type)
                        if channel_data:
                            bot.snowcaloid.data.tasks.add_task(entry.timestamp - timedelta(minutes=30), TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild, "entry_id": entry.id})
                        channel_data = guild_data.get_support_channel(type=entry.type)
                        if channel_data:
                            bot.snowcaloid.data.tasks.add_task(entry.timestamp - timedelta(minutes=35), TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild, "entry_id": entry.id})
                else:
                    entry.pass_main = 0
                    entry.pass_supp = 0
                    guild_data = bot.snowcaloid.data.guild_data.get_data(self.guild)
                    if guild_data:
                        channel_data = guild_data.get_channel(type=entry.type)
                        if channel_data:
                            bot.snowcaloid.data.tasks.remove_task_by_data(TaskExecutionType.POST_MAIN_PASSCODE, {"guild": self.guild, "entry_id": entry.id})
                        channel_data = guild_data.get_support_channel(type=entry.type)
                        if channel_data:
                            bot.snowcaloid.data.tasks.remove_task_by_data(TaskExecutionType.POST_SUPPORT_PASSCODE, {"guild": self.guild, "entry_id": entry.id})
                if set_str:
                    set_str += f', pass_main={str(entry.pass_main)}, pass_supp={str(entry.pass_supp)} '
                else:
                    set_str += f'pass_main={str(entry.pass_main)}, pass_supp={str(entry.pass_supp)} '
                if leader:
                    entry.leader = leader
                    set_str += f', leader={str(leader)}'
                if type:
                    entry.type = type
                    set_str += f', type=\'{type}\''
                if description:
                    entry.description = description
                    set_str += f', description=\'{description}\''
                db = bot.snowcaloid.data.db
                db.connect()
                try:
                    db.query(f'update schedule set {set_str} where id={id}')
                finally:
                    db.disconnect()
            else:
                raise Error_Insufficient_Permissions()
        else:
            raise Error_Invalid_Schedule_Id()

    async def remove_entry(self, leader: int, admin: bool, id: int):
        """Remove the event <id>.

        Args:
            leader (int): User ID of the user trying to edit the entry.
            admin (bool): Does the calling user have admin rights / rights to edit other's runs?
            id (int): event id

        Raises:
            Error_Cannot_Remove_Schedule: The user doesn't have permissions to change the event.
        """
        db = bot.snowcaloid.data.db
        db.connect()
        try:
            u = db.query(f'select leader from schedule where id={id}')[0][0]
            if u == leader or admin:
                db.query(f'delete from schedule where id={id}')
                await self.update_post()
            else:
                raise Error_Cannot_Remove_Schedule()
        finally:
            db.disconnect()
        self.remove(id)

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
        channel: TextChannel = bot.snowcaloid.get_channel(self.channel)
        if channel:
            post = await cache.messages.get(self.post, channel)
            if post:
                embed = post.embeds[0]
                embed.clear_fields()
                self._list.sort(key=lambda d: d.timestamp)
                per_date = self.split_per_date()
                for data in per_date:
                    schedule_on_day = ''
                    for entry in data._list:
                        schedule_on_day = "\n".join([schedule_on_day,
                                                    entry.timestamp.strftime("%H:%M") + f' ST ({get_discord_timestamp(entry.timestamp)} LT): {schedule_type_desc(entry.type)} (Leader: {await get_mention(self.guild, entry.leader)})'])
                        if entry.description:
                            schedule_on_day += f' [{entry.description}]'
                    embed.add_field(name=data._date.strftime("%A, %d %B %Y"), value=schedule_on_day.lstrip("\n"))

                await post.edit(embed=embed)
                await set_default_footer(post)
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
        if entry is None:
            if post_id:
                entry = self.get_entry_by_pl_post(post_id)
            elif id:
                entry = self.get_entry(id)
            else:
                raise Exception('missing entry in update_pl_post')
        if not message:
            pl_channel = guild_data.get_pl_channel(entry.type)
            if pl_channel:
                channel: TextChannel = bot.snowcaloid.get_channel(pl_channel.channel_id)
                message = await cache.messages.get(entry.post_id, channel)
        if message:
            embed = Embed(title=entry.timestamp.strftime('%A, %d %B %Y %H:%M ') + schedule_type_desc(entry.type) + "\nParty leader recruitment")
            embed.description = (
                f'Raid Leader: {await get_mention(self.guild, entry.leader)}\n'
                f'Party 1: {await get_mention(self.guild, entry.party_leaders[0])}\n'
                f'Party 2: {await get_mention(self.guild, entry.party_leaders[1])}\n'
                f'Party 3: {await get_mention(self.guild, entry.party_leaders[2])}\n'
                f'Party 4: {await get_mention(self.guild, entry.party_leaders[3])}\n'
                f'Party 5: {await get_mention(self.guild, entry.party_leaders[4])}\n'
                f'Party 6: {await get_mention(self.guild, entry.party_leaders[5])}\n'
                f'Support: {await get_mention(self.guild, entry.party_leaders[6])}\n\n'
                '*Use the button to volunteer to host a party.\n'
                'Please note, your entry may be removed at the Raid Leader\'s discretion.*'
            )
            message = await message.edit(embed=embed)
            await set_default_footer(message)


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
            channel: TextChannel = bot.snowcaloid.get_channel(pl_channel.channel_id)
            message = await channel.send(f'Recruitment post #{str(id)}')
            entry.post_id = message.id
            view = PersistentView()
            for i in range(1, 7):
                button = PartyLeaderButton(label=str(i), custom_id=button_custom_id(f'pl{i}', message, ButtonType.PL_POST), row=1 if i < 4 else 2)
                view.add_item(button)
            view.add_item(PartyLeaderButton(label='Support', custom_id=button_custom_id('pl7', message, ButtonType.PL_POST), row=2))
            await self.update_pl_post(guild_data, entry=entry, message=message)
            await message.edit(view=view)
            bot.snowcaloid.data.tasks.add_task(entry.timestamp + timedelta(hours=12), TaskExecutionType.REMOVE_OLD_PL_POSTS, {"guild": self.guild, "channel": channel.id})
            bot.snowcaloid.data.db.connect()
            try:
                bot.snowcaloid.data.db.query(f'update schedule set post_id={entry.post_id} where id={id}')
                for button in view.children:
                    bot.snowcaloid.data.db.query(f'insert into buttons values (\'{button.custom_id}\', \'{button.label}\')')
            finally:
                bot.snowcaloid.data.db.disconnect()
        else:
            print(f'Info: no party leader post has been made due to the missing channel for type {type} in guild {bot.snowcaloid.get_guild(self.guild).name}')


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

    def add_entry(self, guild: int, leader: int, type: ScheduleType, timestamp: datetime, description: str = '', auto_passcode: bool = True) -> ScheduleData:
        """Add an event to the guild's schedule.

        Args:
            guild (int): guild id for the schedule post
            leader (int): Event leader (user id). Typically the caller of /schedule_add
            type (ScheduleType): Type of event that is being scheduled.
            timestamp (datetime): When is the run taking place?
            description (str, optional): Description for the run. Defaults to ''.

        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.

        Returns:
            ScheduleData: the event object.
        """
        if self.contains(guild):
            return self.get_post(guild).add_entry(leader, type, timestamp, description, auto_passcode)
        else:
            raise Error_Missing_Schedule_Post()

    def edit_entry(self, id: int, guild: int, leader: int, type: ScheduleType, date: datetime, time: datetime, description: str, passcode: bool, is_admin: bool) -> int:
        """Edits the event.

        Args:
            id (int): event id.
            guild (int): guild id for the schedule post
            leader (int): User ID of the user trying to edit the entry.
            type (ScheduleType): Event type
            date (datetime): Date of the event
            time (datetime): Time of the event
            description (str): Description of the event
            passcode (bool): Is the passcode needed?
            is_admin (bool): Does the calling user have admin rights / rights to edit other's runs?

        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.

        """
        if self.contains(guild):
            return self.get_post(guild).edit_entry(id, leader, type, date, time, description, passcode, is_admin)
        else:
            raise Error_Missing_Schedule_Post()

    async def remove_entry(self, guild: int, leader: int, admin: bool, id: int):
        """Remove the event <id>.

        Args:
            guild (int): guild id for the schedule post
            leader (int): User ID of the user trying to edit the entry.
            admin (bool): Does the calling user have admin rights / rights to edit other's runs?
            id (int): event id

        Raises:
            Error_Missing_Schedule_Post: Guild is missing a schedule post.
        """
        if self.contains(guild):
            await self.get_post(guild).remove_entry(leader, admin, id)
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

    def save(self, guild: int, channel: int, post: int):
        """Saves the schedule post to the runtime object and the database.

        Args:
            guild (int): guild id.
            channel (int): Schedule post channel id.
            post (int): Schedule post message id.
        """
        self._list.append(SchedulePost(guild, channel, post))
        self.guild_data.save_schedule_post(guild, channel, post)

    async def load(self):
        """Loads all schedule posts and events from the database."""
        db = bot.snowcaloid.data.db
        db.connect()
        try:
            self._list.clear()
            for guild_data in self.guild_data._list:
                if guild_data.schedule_post:
                    schedule_post = SchedulePost(guild_data.guild_id, guild_data.schedule_channel, guild_data.schedule_post)
                    for sch_record in db.query(f'select id, leader, type, timestamp, description, post_id, pl1, pl2, pl3, pl4, pl5, pl6, pls, pass_main, pass_supp from schedule where schedule_post={guild_data.schedule_post}'):
                        entry = schedule_post.add_entry(sch_record[1], sch_record[2], sch_record[3], sch_record[4])
                        entry.id = sch_record[0]
                        entry.post_id = sch_record[5]
                        entry.party_leaders = [sch_record[6], sch_record[7], sch_record[8], sch_record[9], sch_record[10], sch_record[11], sch_record[12]]
                        entry.pass_main = sch_record[13]
                        entry.pass_supp = sch_record[14]
                    self._list.append(schedule_post)
                    await schedule_post.update_post()
        finally:
            db.disconnect()
