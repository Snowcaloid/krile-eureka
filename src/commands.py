from bot import snowcaloid
from discord import Interaction, InteractionResponse, Embed
from discord.channel import TextChannel
from discord.ui import View, Button
from discord.app_commands import check, Choice
from buttons import RoleSelectionButton
from data.table.database import DatabaseOperation
from views import PersistentView
from data.query import QueryType
from data.schedule_post_data import Error_Missing_Schedule_Post, Error_Cannot_Remove_Schedule
from data.table.schedule import ScheduleType, schedule_type_desc
from calendar import monthrange, month_abbr
from datetime import date, datetime
from typing import Optional, Union

class DateValueError(ValueError):
    pass

class TimeValueError(ValueError):
    pass

def permission_admin(interaction: Union[Interaction, InteractionResponse]) -> bool:
    for role in interaction.user.roles:
        if role.permissions.administrator:
            return True
    return False

###################################################################################
# role_post
###################################################################################

@snowcaloid.tree.command(name = "role_post_create", description = "Initialize creation process of a role reaction post.")
@check(permission_admin)
async def role_post_create(interaction: InteractionResponse):
    snowcaloid.data.query.start(interaction.user.id, QueryType.ROLE_POST)
    await interaction.response.send_message(
        embed=Embed(title='Use /role_post_add to add roles to the post.'),
        ephemeral=True)

@snowcaloid.tree.command(name = "role_post_finish", description = "Finish and post the role reaction post.")
@check(permission_admin)
async def role_post_finish(interaction: InteractionResponse, channel: TextChannel):
    if not snowcaloid.data.query.running(interaction.user.id, QueryType.ROLE_POST):
        await interaction.response.send_message(
            embed=Embed(title='Use /role_post_create to start the creation process.'),
            ephemeral=True)
        return
    
    view = PersistentView()
    for entry in snowcaloid.data.role_posts.get_entries(interaction.user.id):
        view.add_item(RoleSelectionButton(label=entry.label, custom_id=entry.id))

    await interaction.response.send_message(f'A message will been sent to #{channel.name}.', ephemeral=True)
    channels = await interaction.guild.fetch_channels()
    for ch in channels:
        if ch == channel:
            message = await channel.send(view=view, embed=Embed(title='You can press on the buttons to get roles.'))
            print(f'Message ID: {message.id}, Channel ID: {message.channel.id}, Guild ID: {message.guild.id}')

    snowcaloid.data.query.stop(interaction.user.id, QueryType.ROLE_POST)
    
@snowcaloid.tree.command(name = "role_post_add", description = "Add roles to the reaction post.")
@check(permission_admin)
async def role_post_add(interaction: InteractionResponse, name: str):
    if not snowcaloid.data.query.running(interaction.user.id, QueryType.ROLE_POST):
        await interaction.response.send_message(
            embed=Embed(title='Use /role_post_create to start the creation process.'),
            ephemeral=True)
        return
    
    if name in snowcaloid.data.role_posts.get_entries(interaction.user.id):
        await interaction.response.send_message(
            embed=Embed(title=f'{name} is already in the list. Try another name.'),
            ephemeral=True)
        return
    
    view = View()
    id = str(interaction.guild_id) + str(interaction.user.id) + name
    snowcaloid.data.role_posts.append(interaction.user.id, name, id)
    for entry in snowcaloid.data.role_posts.get_entries(interaction.user.id):
        view.add_item(Button(label=entry.label, disabled=True))
        
    await interaction.response.send_message(
        embed=Embed(title='Use /role_post_create to add more roles, or /role_post_finish to finish.'), 
        view=view,
        ephemeral=True)
    
###################################################################################
# schedule
###################################################################################

@snowcaloid.tree.command(name = "schedule_post_create", description = "Create a static post that will be used as a schedule list. Up to 1 per server.")
@check(permission_admin)
async def schedule_post_create(interaction: InteractionResponse, channel: TextChannel):
    if snowcaloid.data.schedule_posts.contains(interaction.guild_id):
        await interaction.response.send_message('This guild already contains a schedule post.', ephemeral=True)
    else:    
        message = await channel.send('This post contains an embed containing the schedule.', 
                                    embed=Embed(title='Schedule'))
        snowcaloid.data.schedule_posts.save(snowcaloid.data.db, interaction.guild_id, channel.id, message.id)
        await interaction.response.send_message(f'Schedule has been created in #{channel.name}', ephemeral=True)

@snowcaloid.tree.command(name = "schedule_add", description = "Add an entry to the schedule.")
@check(permission_admin)
async def schedule_add(interaction: InteractionResponse, type: str, 
                       event_date: str, event_time: str, description: Optional[str] = ''):
    try:
        try:
            dt = datetime.strptime(event_date, "%d-%b-%Y")
        except:
            raise DateValueError()
        try:
            tm = datetime.strptime(event_time, "%H:%M")
        except:
            raise TimeValueError()
        if not type in ScheduleType._value2member_map_:
            return await interaction.response.send_message(f'The type "{type}" is not allowed. Use autocomplete.', ephemeral=True)
        dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        id = snowcaloid.data.schedule_posts.add_entry(snowcaloid.data.db, 
                                                    interaction.guild_id, 
                                                    interaction.user.id,
                                                    type, dt, description)
        await snowcaloid.data.schedule_posts.update_post(interaction.guild_id, snowcaloid)
        await interaction.response.send_message(f'The run #{str(id)} has been scheduled.')
    except Error_Missing_Schedule_Post:
        await interaction.response.send_message('This server has no schedule post. This is required for scheduling.', ephemeral=True)
    except DateValueError:
        await interaction.response.send_message(f'The date format is not correct. If you start typing in format DD-MM-YYYY, auto-fill will help you.', ephemeral=True)
    except TimeValueError:
        await interaction.response.send_message(f'The time format is not correct. If you start typing in format HH:MM, auto-fill will help you.', ephemeral=True)
    
@snowcaloid.tree.command(name = "schedule_remove", description = "Remove a schedule entry.")
@check(permission_admin)
async def schedule_remove(interaction: InteractionResponse, id: int):
    try:
        await snowcaloid.data.schedule_posts.remove_entry(snowcaloid.data.db, snowcaloid, interaction.guild_id, interaction.user.id, permission_admin(interaction), id)
        await interaction.response.send_message(f'Run #{id} has been deleted.')
    except Error_Missing_Schedule_Post:
        await interaction.response.send_message('This server has no schedule post. This is required for scheduling.', ephemeral=True)
    except Error_Cannot_Remove_Schedule:
        await interaction.response.send_message(f'Run #{id} is not owned by you and you do not have the sufficient rights to remove it.', ephemeral=True)
    except IndexError:
        await interaction.response.send_message(f'The run #{id} doesn\'t exist.', ephemeral=True)
        
@snowcaloid.tree.command(name = "schedule_channel", description = "Set the channel for specific type of events.")
@check(permission_admin)
async def schedule_channel(interaction: InteractionResponse, type: str, channel: TextChannel):
    if not type in ScheduleType._value2member_map_:
        return await interaction.response.send_message(f'The type "{type}" is not allowed. Use autocomplete.', ephemeral=True)
    op = snowcaloid.data.guild_data.set_schedule_channel(snowcaloid.data.db, interaction.guild_id, type, channel.id)
    if op == DatabaseOperation.EDITED:
        await interaction.response.send_message(f'You have changed the post channel for type "{schedule_type_desc(type)}" to #{channel.name}.', ephemeral=True)
    else:
        await interaction.response.send_message(f'You have set #{channel.name} as the post channel for type "{schedule_type_desc(type)}".', ephemeral=True)
        
###################################################################################
# autocomplete
###################################################################################

@schedule_add.autocomplete('type')
@schedule_channel.autocomplete('type')
async def autocomplete_schedule_type(interaction: Interaction, current: str):
    return [
        Choice(name='BA Normal Run',  value=ScheduleType.BA_NORMAL.value),
        Choice(name='BA Reclear Run', value=ScheduleType.BA_RECLEAR.value),
        Choice(name='BA Special Run', value=ScheduleType.BA_SPECIAL.value)        
    ]
    
@schedule_add.autocomplete('event_date')
async def autocomplete_schedule_date(interaction: Interaction, current: str):
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

@schedule_add.autocomplete('event_time')
async def autocomplete_schedule_time(interaction: Interaction, current: str):
    result = []
    if len(current) >= 2 and current[0:2].isdigit(): 
        hour = int(current[0:2])
        if hour < 24 and hour >= 0:
            for i in range(0, 60, 5):
                dt = f'{str(hour)}:{str(i).zfill(2)}'
                result.append(Choice(name=dt, value=dt))
    return result             
    
###################################################################################
# permission error handling
###################################################################################

@role_post_create.error
@role_post_add.error
@role_post_finish.error
@schedule_post_create.error
async def handle_permission_admin(interaction: Interaction, error):
    await interaction.response.send_message('Using this command requires administrator privileges.', ephemeral=True)

def so_that_import_works():
    return