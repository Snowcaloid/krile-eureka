from typing import Callable, Optional
from models.context import ExecutionContext
from discord import Interaction
from models.permissions import Permissions
from data_providers.permissions import PermissionProvider
from utils.logger import BaseLogger, GuildLogger

def basic_context(user_id: int,
                  guild_id: int,
                  logger: BaseLogger,
                  permissions: Optional[Permissions] = None,
                  on_flush: Optional[Callable[...]] = None) -> ExecutionContext:
    return ExecutionContext(user_id=user_id,
                            guild_id=guild_id,
                            logger=logger,
                            permissions=permissions,
                            on_flush=on_flush)

def discord_context(interaction: Interaction) -> ExecutionContext:
    guild_id = interaction.guild_id
    assert guild_id is not None, 'Interaction must be in a guild context'
    return basic_context(user_id=interaction.user.id,
                         guild_id=guild_id,
                         logger=GuildLogger(guild_id),
                         permissions=PermissionProvider().evaluate_permissions_for_user(guild_id, interaction.user.id),
                         on_flush=lambda message, exc: GuildLogger(guild_id).respond(interaction, message))