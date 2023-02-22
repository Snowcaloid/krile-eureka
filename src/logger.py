import time

import bot


async def guild_log_message(guild_id: int, message: str):
    """Send a log message to the specified guild if it has a log channel set.

    Args:
            guild_id (int): the id of the guild to send a log message to
            message (str): the message to log
    """
    # Retrieve the log channel id for this guild
    guild_data = bot.snowcaloid.data.guild_data.get_data(guild_id)

    if guild_data.log_channel is None:
        # Cannot send logging messages if a channel has not been set
        return

    guild = bot.snowcaloid.get_guild(guild_id)

    if guild is None:
        return

    channel = await guild.fetch_channel(guild_data.log_channel)

    if channel is None:
        return

    # Print the log message with a timestamp
    await channel.send(f'<t:{int(time.time())}:t> {message}')
