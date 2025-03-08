
from typing import List, override
from centralized_data import GlobalCollection
from discord import ChannelType


class SimpleGuild:
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    from data.validation.permission_validator import PermissionValidator
    @PermissionValidator.bind
    def _permissions(self) -> PermissionValidator: ...

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

    def marshal(self) -> dict:
        guild = self._bot.client.get_guild(self.id)
        raid_leaders = []
        for member in guild.members:
            categories = self._permissions.get_raid_leader_permissions(member)
            if categories:
                raid_leaders.append({
                    'id': str(member.id),
                    'name': member.display_name,
                    'categories': [category.value for category in categories]
                })
        return {
            'id': str(self.id),
            'name': self.name,
            'channels': [{'id': str(channel.id), 'name': channel.name}
                         for channel in guild.channels if channel.type == ChannelType.text],
            'roles': [{'id': str(role.id), 'name': role.name} for role in guild.roles],
            'raid_leaders': raid_leaders
        }

class GuildManager(GlobalCollection[int]):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    @override
    def constructor(self, key: int) -> None:
        super().constructor(key)
        self._guilds: List[SimpleGuild] = []
        self.load()

    def load(self) -> None:
        self._guilds.clear()
        user = self.bot.client.get_user(self.key)
        if user is None: return
        for guild in user.mutual_guilds:
            self._guilds.append(SimpleGuild(guild.id, guild.name))

    @property
    def all(self) -> List[SimpleGuild]:
        return self._guilds