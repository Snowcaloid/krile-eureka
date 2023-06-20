import bot
import data.message_cache as cache
from typing import List
from discord import Embed, TextChannel
from data.table.missed import MissedData

class MissedRunsData:
    """Runtime data object containing information
    about missed runs.

    Properties
    ----------
    _list: :class:`List[MissedData]`
        List of all missed data informations.
    """
    _list: List[MissedData]

    def __init__(self) -> None:
        self._list = []

    def init(self, guild: int, user: int):
        """Initialize guild-user relation

        Args:
            guild (int): guild id
            user (int): user id
        """
        if not self.get_data(guild, user):
            self._list.append(MissedData(guild, user))

    def get_data(self, guild: int, user: int):
        """Get data for the guild-user relation

        Args:
            guild (int): guild id
            user (int): user id
        """
        for data in self._list:
            if data.guild == guild and data.user == user:
                return data
        return None

    def get_guild_data(self, guild: int) -> List[MissedData]:
        """Get all the missed run data for the guild

        Args:
            guild (int): guild id
        """
        list = []
        for data in self._list:
            if data.guild == guild:
                list.append(data)
        return list

    def eligable(self, guild: int, user: int):
        """Is the user in the guild eligable for a notification?

        Args:
            guild (int): guild id
            user (int): user id
        """
        data = self.get_data(guild, user)
        return data and data.amount >= 3

    def inc(self, guild: int, user: int):
        """Increase the amount of the guild-user relation

        Args:
            guild (int): guild id
            user (int): user id
        """
        self.init(guild, user)
        self.get_data(guild, user).amount += 1
        self.save(guild, user)

    def remove(self, guild: int, user: int):
        """Remove the guild-user relation

        Args:
            guild (int): guild id
            user (int): user id
        """
        self._list.remove(self.get_data(guild, user))
        db = bot.krile.data.db
        db.connect()
        try:
            db.query(f'delete from missed where guild={guild} and user_id={user}')
        finally:
            db.disconnect()

    def save(self, guild: int, user: int):
        """Save the guild-user relation to the database

        Args:
            guild (int): guild id
            user (int): user id
        """
        self.init(guild, user)
        if self.get_data(guild, user).amount:
            db = bot.krile.data.db
            db.connect()
            try:
                if db.query(f'select amount from missed where guild={guild} and user_id={user}'):
                    db.query(f'update missed set amount={self.get_data(guild, user).amount} where guild={guild} and user_id={user}')
                else:
                    db.query(f'insert into missed (guild, user_id, amount) values ({guild}, {user}, {self.get_data(guild, user).amount})')
            finally:
                db.disconnect()

    async def load(self):
        """Load all missed runs data from the database"""
        db = bot.krile.data.db
        db.connect()
        try:
            missed = db.query(f'select guild, user_id, amount from missed')
            for record in missed:
                self._list.append(MissedData(record[0], record[1], record[2]))
        finally:
            db.disconnect()
        for guild_data in bot.krile.data.guild_data._list:
            await self.update_post(guild_data.guild_id)


    async def update_post(self, guild: int):
        """Updates the missed runs post.

        Args:
            guild (int): guild id
        """
        guild_data = bot.krile.data.guild_data.get_data(guild)
        if guild_data.missed_channel and guild_data.missed_post:
            channel: TextChannel = bot.krile.get_channel(guild_data.missed_channel)
            if channel:
                message = await cache.messages.get(guild_data.missed_post, channel)
                embeds = []
                embed = Embed(title='List of people with missing runs')
                embeds.append(embed)
                i = 0
                description = ''
                gld = bot.krile.get_guild(guild)
                for missed_data in self.get_guild_data(guild):
                    i += 1
                    if i % 150 == 0:
                        embed.description = description.strip()
                        embed = Embed()
                        embeds.append(embed)
                        description = ''
                    member = gld.get_member(missed_data.user)
                    if member:
                        description = "\n".join([description, f'{str(missed_data.amount)} - {member.display_name}'])
                if description:
                    embed.description = description.strip()

                await message.edit(embeds=embeds)