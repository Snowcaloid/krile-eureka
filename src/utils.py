from datetime import datetime, timezone
from enum import Enum
import time
from discord import Message
from buttons import ButtonType
from dateutil.tz import tzlocal, tzutc

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