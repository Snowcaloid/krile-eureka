from datetime import datetime
from enum import Enum
import time

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
