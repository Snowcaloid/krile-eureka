import bot
from calendar import monthrange, month_abbr
from discord.ext.commands import GroupCog
from discord.app_commands import check, command, Choice
from discord import Interaction, Embed
from discord.channel import TextChannel
from datetime import date, datetime
from typing import List, Optional
from data.schedule_post_data import Error_Insufficient_Permissions, Error_Invalid_Date, Error_Invalid_Schedule_Id, Error_Missing_Schedule_Post, Error_Cannot_Remove_Schedule
from data.table.database import DatabaseOperation
from data.table.schedule import ScheduleData, ScheduleType, schedule_type_desc
from utils import set_default_footer, default_defer, default_response
from validation import permission_admin, permission_raid_leader, get_raid_leader_permissions
from logger import guild_log_message

class DateValueError(ValueError): pass
class TimeValueError(ValueError): pass

###################################################################################
# schedule
###################################################################################
class ScheduleCommands(GroupCog, group_name='schedule', group_description='Commands regarding scheduling runs.'):
    @command(name = "initialize", description = "Initialize the server\'s schedule by creating a static post that will be used as a schedule list.")
    @check(permission_admin)
    async def initialize(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        if bot.snowcaloid.data.schedule_posts.contains(interaction.guild_id):
            await default_response(interaction, 'This guild already contains a schedule post.')
        else:
            message = await channel.send('This post contains an embed containing the schedule.',
                                        embed=Embed(title='Schedule'))
            await set_default_footer(message)
            bot.snowcaloid.data.schedule_posts.save(interaction.guild_id, channel.id, message.id)
            await default_response(interaction, f'Schedule has been created in #{channel.name}')
            await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has created a schedule post in #{channel.name}.')

    @command(name = "add", description = "Add an entry to the schedule.")
    @check(permission_raid_leader)
    async def add(self, interaction: Interaction, type: str,
                  event_date: str, event_time: str,
                  description: Optional[str] = '',
                  auto_passcode: Optional[bool] = True):
        await default_defer(interaction, False)
        try:
            allow_ba, allow_drs = get_raid_leader_permissions(interaction.user)
            if type.startswith('BA') and not allow_ba:
                return await default_response(interaction, 'You are not a BA raid leader.')
            if type.startswith('DRS') and not allow_drs:
                return await default_response(interaction, 'You are not a DRS raid leader.')
            if type == ScheduleType.CUSTOM.value and not description:
                return await default_response(interaction, 'Description is mandatory for custom runs.')
            if not type in ScheduleType._value2member_map_:
                return await default_response(interaction, f'The type "{type}" is not allowed. Use autocomplete.')
            try:
                dt = datetime.strptime(event_date, "%d-%b-%Y")
            except:
                raise DateValueError()
            try:
                tm = datetime.strptime(event_time, "%H:%M")
            except:
                raise TimeValueError()
            dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
            if dt < datetime.utcnow():
                return await default_response(interaction, f'Date {event_date} {event_time} is invalid or not in future. Use autocomplete.')
            entry: ScheduleData = bot.snowcaloid.data.schedule_posts.add_entry(
                interaction.guild_id,
                interaction.user.id,
                type, dt, description, auto_passcode)
            await bot.snowcaloid.data.schedule_posts.update_post(interaction.guild_id)
            if type != ScheduleType.CUSTOM.value:
                await bot.snowcaloid.data.schedule_posts.create_pl_post(interaction.guild_id, entry.id)
            await default_response(interaction, f'The run #{str(entry.id)} has been scheduled.')
            await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has scheduled a {type} run #{entry.id} for {dt}.')
        except Error_Missing_Schedule_Post:
            await default_response(interaction, 'This server has no schedule post. This is required for scheduling.')
        except DateValueError:
            await default_response(interaction, f'The date format is not correct. If you start typing in format DD-MM-YYYY, auto-fill will help you.')
        except TimeValueError:
            await default_response(interaction, f'The time format is not correct. If you start typing in format HH:MM, auto-fill will help you.')

    @command(name = "remove", description = "Remove a schedule entry.")
    @check(permission_raid_leader)
    async def remove(self, interaction: Interaction, id: int):
        await default_defer(interaction, False)
        try:
            await bot.snowcaloid.data.schedule_posts.remove_entry(interaction.guild_id, interaction.user.id, permission_admin(interaction), id)
            await default_response(interaction, f'Run #{id} has been deleted.')
            await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has deleted the run #{id}.')
        except Error_Missing_Schedule_Post:
            await default_response(interaction, 'This server has no schedule post. This is required for scheduling.')
        except Error_Cannot_Remove_Schedule:
            await default_response(interaction, f'Run #{id} is not owned by you and you do not have the sufficient rights to remove it.')
        except IndexError:
            await default_response(interaction, f'The run #{id} doesn\'t exist.')

    @command(name = "passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted.")
    @check(permission_admin)
    async def passcode_channel(self, interaction: Interaction, type: str, channel: TextChannel):
        await default_defer(interaction)
        if not type in ScheduleType._value2member_map_:
            return await default_response(interaction, f'The type "{type}" is not allowed. Use autocomplete.')
        op = bot.snowcaloid.data.guild_data.set_schedule_channel(interaction.guild_id, type, channel.id)
        if op == DatabaseOperation.EDITED:
            await default_response(interaction, f'You have changed the post channel for type "{schedule_type_desc(type)}" to #{channel.name}.')
        else:
            await default_response(interaction, f'You have set #{channel.name} as the post channel for type "{schedule_type_desc(type)}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has set #{channel.name} as the post channel for type "{schedule_type_desc(type)}".')

    @command(name = "support_passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted (for support parties).")
    @check(permission_admin)
    async def support_passcode_channel(self, interaction: Interaction, type: str, channel: TextChannel):
        await default_defer(interaction)
        if not type in ScheduleType._value2member_map_:
            return await default_response(interaction, f'The type "{type}" is not allowed. Use autocomplete.')
        op = bot.snowcaloid.data.guild_data.set_schedule_support_channel(interaction.guild_id, type, channel.id)
        if op == DatabaseOperation.EDITED:
            await default_response(interaction, f'You have changed the post channel for type "{schedule_type_desc(type)}" to #{channel.name}.')
        else:
            await default_response(interaction, f'You have set #{channel.name} as the post channel for type "{schedule_type_desc(type)}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has set the post channel to #{channel.name} for the "{schedule_type_desc(type)}" type.')

    @command(name = "party_leader_channel", description = "Set the channel for party leader posts.")
    @check(permission_admin)
    async def party_leader_channel(self, interaction: Interaction, type: str, channel: TextChannel):
        await default_defer(interaction)
        if not type in ScheduleType._value2member_map_:
            return await default_response(interaction, f'The type "{type}" is not allowed. Use autocomplete.')
        op = bot.snowcaloid.data.guild_data.set_party_leader_channel(interaction.guild_id, type, channel.id)
        if op == DatabaseOperation.EDITED:
            await default_response(interaction, f'You have changed the party leader recruitment channel for type "{schedule_type_desc(type)}" to #{channel.name}.')
        else:
            await default_response(interaction, f'You have set #{channel.name} as the party leader recruitment channel for type "{schedule_type_desc(type)}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has set the party leader channel to #{channel.name} for the "{schedule_type_desc(type)}" type.')

    @command(name = "edit", description = "Edit an entry from the schedule.")
    @check(permission_raid_leader)
    async def edit(self, interaction: Interaction, id: int, type: Optional[str] = '',
                   leader: Optional[str] = '', event_date: Optional[str] = '',
                   event_time: Optional[str] = '', description: Optional[str] = '',
                   passcode: Optional[bool] = True):
        await default_defer(interaction, False)
        try:
            allow_ba, allow_drs = get_raid_leader_permissions(interaction.user)
            if type.startswith('BA') and not allow_ba:
                return await default_response(interaction, 'You are not a BA raid leader.')
            if type.startswith('DRS') and not allow_drs:
                return await default_response(interaction, 'You are not a DRS raid leader.')
            if type and not type in ScheduleType._value2member_map_:
                return await default_response(interaction, f'The type "{type}" is not allowed. Use autocomplete.')
            dt = None
            tm = None
            if event_date:
                try:
                    dt = datetime.strptime(event_date, "%d-%b-%Y")
                except:
                    raise DateValueError()
            if event_time:
                try:
                    tm = datetime.strptime(event_time, "%H:%M")
                except:
                    raise TimeValueError()
            if dt and tm:
                date = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
                if date < datetime.utcnow():
                    return await default_response(interaction, f'Date {event_date} {event_time} is invalid or not in future. Use autocomplete.')
            bot.snowcaloid.data.schedule_posts.edit_entry(id,
                                                    interaction.guild_id,
                                                    int(leader or 0),
                                                    type, dt, tm, description, passcode,
                                                    permission_admin(interaction))
            await bot.snowcaloid.data.schedule_posts.update_post(interaction.guild_id)
            await bot.snowcaloid.data.schedule_posts.get_post(interaction.guild_id).update_pl_post(bot.snowcaloid.data.guild_data.get_data(interaction.guild_id), id=id)
            await default_response(interaction, f'The run #{str(id)} has been adjusted.')
            await guild_log_message(interaction.guild_id, f'**{interaction.user.name}** has adjusted run #{str(id)}')
        except Error_Invalid_Date:
            await default_response(interaction, f'Date is invalid or not in future. Use autocomplete.')
        except Error_Missing_Schedule_Post:
            await default_response(interaction, 'This server has no schedule post. This is required for scheduling.')
        except Error_Invalid_Schedule_Id:
            await default_response(interaction, f'The run #{id} does\'t exist.')
        except Error_Insufficient_Permissions:
            await default_response(interaction, 'You\'re not allowed to change this run\'s properties. Only the run creator or an admin can do this.')
        except DateValueError:
            await default_response(interaction, f'The date format is not correct. If you start typing in format DD-MM-YYYY, auto-fill will help you.')
        except TimeValueError:
            await default_response(interaction, f'The time format is not correct. If you start typing in format HH:MM, auto-fill will help you.')

    @add.autocomplete('type')
    @edit.autocomplete('type')
    async def autocomplete_schedule_type(self, interaction: Interaction, current: str):
        allow_ba, allow_drs = get_raid_leader_permissions(interaction.user)
        ba_runs = [
            Choice(name='BA Normal Run',  value=ScheduleType.BA_NORMAL.value),
            Choice(name='BA Reclear Run', value=ScheduleType.BA_RECLEAR.value),
            Choice(name='BA Special Run', value=ScheduleType.BA_SPECIAL.value)
        ]
        drs_runs = [
            Choice(name='DRS Normal Run',  value=ScheduleType.DRS_NORMAL.value),
            Choice(name='DRS Reclear Run', value=ScheduleType.DRS_RECLEAR.value)
        ]
        result = [Choice(name='Custom run (define by yourself in description)', value=ScheduleType.CUSTOM.value)]
        if allow_ba:
            result += ba_runs
        if allow_drs:
            result += drs_runs
        return result

    @passcode_channel.autocomplete('type')
    @party_leader_channel.autocomplete('type')
    @support_passcode_channel.autocomplete('type')
    async def autocomplete_schedule_type_with_all(self, interaction: Interaction, current: str):
        allow_ba, allow_drs = get_raid_leader_permissions(interaction.user)
        result = await self.autocomplete_schedule_type(interaction, current)
        if allow_ba:
            result.append(Choice(name='All BA Runs', value=ScheduleType.BA_ALL.value))
        if allow_drs:
            result.append(Choice(name='All DRS Runs', value=ScheduleType.DRS_ALL.value))
        return result

    @edit.autocomplete('leader')
    async def autocomplete_leader(self, interaction: Interaction, current: str):
        result: List[Choice] = []
        for member in interaction.guild.members:
            for role in member.roles:
                if role.permissions.administrator or 'raid lead' in role.name.lower():
                    name = member.name
                    if member.nick:
                        name = f'{member.nick} [{name}]'
                    result.append(Choice(name=name, value=str(member.id)))
                    break
        return result

    @add.autocomplete('event_date')
    @edit.autocomplete('event_date')
    async def autocomplete_schedule_date(self, interaction: Interaction, current: str):
        result = []
        if len(current) >= 2 and current[0:2].isdigit():
            day = int(current[0:2])
            for i in range(1, 12):
                if monthrange(date.today().year, i)[1] >= day and date.today() <= date(date.today().year, i, day):
                    dt = f'{str(day)}-{month_abbr[i]}-{str(date.today().year)}'
                    result.append(Choice(name=dt, value=dt))
            for i in range(1, 12):
                if monthrange(date.today().year + 1, i)[1] >= day:
                    dt = f'{str(day)}-{month_abbr[i]}-{str(date.today().year + 1)}'
                    result.append(Choice(name=dt, value=dt))
        return result

    @add.autocomplete('event_time')
    @edit.autocomplete('event_time')
    async def autocomplete_schedule_time(self, interaction: Interaction, current: str):
        result = []
        if len(current) >= 2 and current[0:2].isdigit():
            hour = int(current[0:2])
            if hour < 24 and hour >= 0:
                for i in range(0, 60, 5):
                    dt = f'{str(hour)}:{str(i).zfill(2)}'
                    result.append(Choice(name=dt, value=dt))
        return result