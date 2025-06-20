

from centralized_data import Bindable
from models.channel_assignment import ChannelAssignmentStruct
from models.context import ExecutionContext
from models.role_assignment import RoleAssignmentStruct
from data_providers.channel_assignments import ChannelAssignmentProvider
from data_providers.role_assignments import RoleAssignmentsProvider
from tasks import Tasks
from utils.basic_types import (
    NOTORIOUS_MONSTERS, ChannelDenominator, ChannelFunction,
    NotoriousMonster, RoleDenominator, RoleFunction
)


class EurekaPingWorkflow(Bindable):
    """Worker for pinging about Eureka-related notorious monster spawns."""

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def execute(self, notorious_monster: NotoriousMonster,
                message: str,
                context: ExecutionContext) -> None:
        with context:
            context.log(f'Pinging for notorious monster: {NOTORIOUS_MONSTERS[notorious_monster]} with message: {message}')
            for guild in self._bot.guilds:
                channel_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
                    guild_id=guild.id,
                    denominator=ChannelDenominator.NOTORIOUS_MONSTER,
                    notorious_monster=notorious_monster,
                    function=ChannelFunction.NM_PINGS,
                ))
                if channel_struct is None: continue
                role_mention_string = RoleAssignmentsProvider().as_discord_mention_string(RoleAssignmentStruct(
                    guild_id=guild.id,
                    denominator=RoleDenominator.NOTORIOUS_MONSTER,
                    notorious_monster=notorious_monster,
                    function=RoleFunction.NOTORIOUS_MONSTER_NOTIFICATION
                ))
                channel = self._bot.get_text_channel(channel_struct.channel_id)
                Tasks.run_async_method(
                    channel.send,
                    *[
                        (
                            f'{role_mention_string} Notification for '
                            f'{NOTORIOUS_MONSTERS[notorious_monster]} by '
                            f'{self._bot.get_user(context.user_id).mention}: {message}'
                        )
                    ]
                )
                context.log(f'Sent ping to {channel.jump_url} ({guild.name} | #{channel.name}).')
