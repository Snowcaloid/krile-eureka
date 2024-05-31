from datetime import datetime, timedelta
import time
from typing import List
from discord import Guild, Interaction, Message, Member, Role
from dateutil.tz import tzlocal, tzutc
from enum import Enum
# DO NOT IMPORT OTHER UNITS FROM /src/!
import bot


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


async def get_mention(guild_id: int, user_id: int) -> str:
    if user_id:
        guild = bot.instance.get_guild(guild_id)
        if guild:
            return guild.get_member(user_id).mention
    else:
        return ''


async def get_discord_member(guild_id: int, user_id: int) -> Member:
    """Get a discord member object to work with.
    Useful for retrieving the username and mentions.

    :param guild_id: The ID of the guild.
    :param user_id: The ID of the user.
    :return: The discord.Member object.
    """
    guild = bot.instance.get_guild(guild_id)
    return await guild.fetch_member(user_id)


async def set_default_footer(message: Message):
    if message and message.embeds:
        message.embeds[len(message.embeds) - 1].set_footer(text=f'Message ID: {str(message.id)}')
        return await message.edit(embeds=message.embeds)

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

def sql_int(value: int) -> str:
    return 'null' if value is None else str(value)

def find_nearest_role(guild: Guild, role_name: str) -> Role:
    return next(role for role in guild.roles if role.name.lower().startswith(role_name.lower()))