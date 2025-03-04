
from typing import List, override
from centralized_data import GlobalCollection


class SimpleGuild:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

class GuildManager(GlobalCollection[int]):
    from bot import DiscordClient
    @DiscordClient.bind
    def client(self) -> DiscordClient: ...

    @override
    def constructor(self, key: int) -> None:
        super().constructor(key)
        self._guilds: List[SimpleGuild] = []
        self.load()

    def load(self) -> None:
        self._guilds.clear()
        user = self.client.get_user(self.key)
        if user is None: return
        for guild in user.mutual_guilds:
            self._guilds.append(SimpleGuild(guild.id, guild.name))

    @property
    def all(self) -> List[SimpleGuild]:
        return self._guilds