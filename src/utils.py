from datetime import datetime
from enum import Enum
import time
from discord import Message
from buttons import ButtonType

class UnixStamp(Enum):
    TIME = 0
    RELATIVE = 1

def unix_time(date: datetime, type: UnixStamp = UnixStamp.TIME) -> str:
    date_tuple = (date.year, date.month, date.day, date.hour, date.minute, date.second)
    t = ''
    if type == UnixStamp.TIME:
        t = 't'
    elif type == UnixStamp.RELATIVE:
        t = 'R'
    return f'<t:{int(time.mktime(datetime(*date_tuple).timetuple()))}:{t}>'

def button_custom_id(id: str, message: Message, type: ButtonType) -> str:
    return f'{message.id}-{type.value}-{id}'