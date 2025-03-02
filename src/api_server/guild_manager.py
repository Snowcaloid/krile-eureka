
from typing import List, override
from centralized_data import GlobalCollection, Singleton
from discord.ext.commands import Bot

from api_server.login_manager import LoginManager
from basic_types import UserUUID

class SimpleGuild:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name

class GuildManager(GlobalCollection[UserUUID]):
    @LoginManager.bind
    def login_manager(self) -> LoginManager: ...

    @override
    def constructor(self, key: UserUUID) -> None:
        super().constructor(key)
        self._guilds: List[SimpleGuild] = []

    def load(self) -> None:
        self._guilds.clear()
        user = self.login_manager.get_user(self.key)
        if user is None: return
        client: Bot = Singleton.get_instance(Bot)
        for guild in client.guilds:
            self._guilds.append(SimpleGuild(guild.id, guild.name))