

from typing import override
from models.channel import ChannelStruct
from models.context import ExecutionContext
from models.roles import RoleStruct
from providers.channels import ChannelsProvider
from providers.roles import RolesProvider
from utils.basic_types import NOTORIOUS_MONSTERS, GuildChannelFunction, RoleFunction
from workers._base import BaseWorker


class EurekaPingsWorker(BaseWorker):
    """Worker for pinging about Eureka-related notorious monster spawns."""

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    from user_input.notorious_monster import NotoriousMonsterUserInput
    @NotoriousMonsterUserInput.bind
    def _notorious_monster_user_input(self) -> NotoriousMonsterUserInput: ...

    @override
    def execute(self, nm: str,
                message: str,
                context: ExecutionContext) -> None:
        with context:
            notorious_monster = self._notorious_monster_user_input.validate_and_fix(nm)
            for guild in self._bot._client.guilds:
                channel_struct = ChannelsProvider().find(ChannelStruct(
                    guild_id=guild.id,
                    event_type=notorious_monster.value,
                    function=GuildChannelFunction.NM_PINGS
                ))
                if channel_struct is None: continue
                channel = self._bot._client.get_channel(channel_struct.channel_id)
                if channel is None: continue
                role_mention_string = RolesProvider().as_discord_mention_string(RoleStruct(
                    guild_id=guild.id,
                    event_type=notorious_monster.value,
                    function=RoleFunction.NM_PING
                ))
                channel.send(
                    f"{role_mention_string} Notification for {NOTORIOUS_MONSTERS[notorious_monster]} by {
                        self._bot._client.get_user(context.user_id).mention}: {message}"
                )