
from typing import List, override
from centralized_data import GlobalCollection, Singleton
from discord.ext.commands import Bot


class SimpleGuild:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

class GuildManager(GlobalCollection[int]):
    @override
    def constructor(self, key: int) -> None:
        super().constructor(key)
        self._guilds: List[SimpleGuild] = []
        self.load()

    def load(self) -> None:
        self._guilds.clear()
        client: Bot = Singleton.get_instance(Bot)
        #user = synchronize(client.fetch_user(self.key), client.loop)
        user = client.get_user(self.key)
        if user is None: return
        for guild in client.get_user(self.key).mutual_guilds:
            self._guilds.append(SimpleGuild(guild.id, guild.name))

    @property
    def all(self) -> List[SimpleGuild]:
        return self._guilds