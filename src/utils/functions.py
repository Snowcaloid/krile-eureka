from datetime import datetime, timedelta
from random import randint, seed
import time
from typing import Any, List, Type
from discord.app_commands import Choice
from discord import Guild, Interaction, Role
from dateutil.tz import tzlocal, tzutc
from enum import Enum

from utils.basic_types import Unassigned

class DiscordTimestampType(Enum):
    """Enum for the discord timestamp display format."""
    RELATIVE = 'R'
    """Relative time (e.g. 2 months ago, in an hour)"""
    SHORT_TIME = 't'
    """Short time (e.g. 09:41 PM)"""
    LONG_TIME = 'T'
    """Long time (e.g. 09:41:30 PM)"""
    SHORT_DATE = 'd'
    """Short date (e.g. 30/06/2023)"""
    LONG_DATE = 'D'
    """Long date (e.g. 30 June 2023)"""
    SHORT_DATE_TIME = 'f'
    """Short date and time (e.g. 30 June 2023 09:41 PM)"""
    LONG_DATE_TIME = 'F'
    """Long date and time (e.g. Friday, 30 June 2023 09:41"""


def get_discord_timestamp(date: datetime, timestamp_type: DiscordTimestampType = DiscordTimestampType.SHORT_TIME) -> str:
    """Returns a string that can be inserted into text, showing the
    end user's local time."""
    dt = date.replace(tzinfo=tzutc()).astimezone(tzlocal())
    date_tuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return f'<t:{int(time.mktime(datetime(*date_tuple).timetuple()))}:{timestamp_type.value}>'


async def default_defer(interaction: Interaction, ephemeral: bool = True):
    await interaction.response.defer(thinking=True, ephemeral=ephemeral)


async def default_response(interaction: Interaction, text: str):
    return await interaction.followup.send(text, wait=True)


def decode_emoji(emoji: str) -> str:
    return emoji.encode('ascii').decode('unicode-escape').encode('utf-16', 'surrogatepass').decode('utf-16')


def delta_to_string(delta: timedelta) -> str:
    hours = delta.seconds // 3600
    minutes = (delta.seconds - (hours * 3600)) // 60
    result = f'{str(hours)} hours, {str(minutes)} minutes'
    if delta.days:
        result = f'{str(delta.days)} days, {result}'
    return result


def find_nearest_role(guild: Guild, role_name: str) -> Role:
    return next(role for role in guild.roles if role.name.lower().startswith(role_name.lower()))


def user_display_name(guild_id: int, user_id: int) -> str:
    from bot import Bot
    if user_id is None or user_id < 1: return ''
    guild = Bot()._client.get_guild(guild_id)
    if guild is None: return ''
    member = guild.get_member(user_id)
    if member is None: return ''
    return member.display_name


def is_null_or_unassigned(value: Any) -> bool:
    from utils.basic_types import Unassigned
    return value is None or value is Unassigned


def filter_choices_by_current(list: List[Choice[Any]], current: str) -> List[Choice]:
    if current == '':
        return list[:25]
    else:
        return [choice for choice in list if choice.name.lower().startswith(current.lower())][:25]


def generate_passcode(change_seed: bool = True) -> int:
    if change_seed:
        seed(datetime.utcnow().toordinal())
    return int(''.join(str(randint(0, 9)) for _ in range(4)))


def fix_enum(enum_type: Type[Enum], value: Any):
    if isinstance(value, enum_type):
        return value
    else:
        return enum_type(value) if value is not None and value is not Unassigned else None