import os
import time
from datetime import datetime

import bot


async def guild_log_message(guild_id: int, message: str):
    """Send a log message to the specified guild if it has a log channel set.

    Args:
            guild_id (int): the id of the guild to send a log message to
            message (str): the message to log
    """
    # Retrieve the log channel id for this guild
    guild_data = bot.krile.data.guild_data.get_data(guild_id)

    if guild_data.log_channel is None:
        # Cannot send logging messages if a channel has not been set
        return

    guild = bot.krile.get_guild(guild_id)

    if guild is None:
        return

    channel = guild.get_channel(guild_data.log_channel)

    if channel is None:
        return

    # Print the log message with a timestamp
    await channel.send(f'<t:{int(time.time())}:t> {message}')

    # Write this message to a log file
    await output_to_file(guild_id, message)


async def output_to_file(guild_id: int, message: str):
    """Write a log message to a file.

    Args:
        guild_id (int): the id of the guild to write the log message to
        message (str): the message to log

    Returns:
        None
    """
    # Get the log file format and replace the guild id placeholder
    log_file = os.getenv('LOG_FILE_FORMAT')

    if log_file is None or log_file == '':
        return

    # Set the guild id placeholder (do we want a guild_name placeholder too?)
    log_file = log_file.replace('{guild_id}', str(guild_id))

    datetime_now = datetime.now()

    # Replace the time format placeholders with the current time
    log_file = datetime_now.strftime(log_file)

    # Get a date time prefix for the log message
    log_time = datetime_now.strftime('%Y-%m-%d %H:%M:%S')

    # Ensure the directory exists before writing to the file
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Write the message to the file
    with open(log_file, 'a') as file:
        file.write(f'[{log_time}] {message}{os.linesep}')
