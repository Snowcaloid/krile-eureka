from datetime import datetime
from enum import Enum
import time
from discord import Message
from buttons import ButtonType
from dateutil.tz import tzlocal, tzutc
import bot as u_bot

class UnixStamp(Enum):
    TIME = 0
    RELATIVE = 1

def unix_time(date: datetime, type: UnixStamp = UnixStamp.TIME) -> str:
    """Returns a string string that can be inserted into text, showing the 
    end user's local time."""
    dt = date.replace(tzinfo=tzutc()).astimezone(tzlocal())
    date_tuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    t = ''
    if type == UnixStamp.TIME:
        t = 't'
    elif type == UnixStamp.RELATIVE:
        t = 'R'
    return f'<t:{int(time.mktime(datetime(*date_tuple).timetuple()))}:{t}>'

def button_custom_id(id: str, message: Message, type: ButtonType) -> str:
    """Generate custom_id for a button."""
    return f'{message.id}-{type.value}-{id}'

async def get_mention(guild_id: int, user_id: int) -> str: 
    if user_id:
        guild = u_bot.snowcaloid.get_guild(guild_id)
        if guild:
            return (await guild.fetch_member(user_id)).mention
    else:
        return ''
    
async def set_default_footer(message: Message):
    if message and message.embeds:
        message.embeds[len(message.embeds) - 1].set_footer(text=f'Message ID: {str(message.id)}')
        await message.edit(embeds=message.embeds)