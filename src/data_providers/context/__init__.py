from models.context import ExecutionContext
from discord import Interaction
from models.permissions import Permissions
from data_providers.permissions import PermissionProvider
from utils.logger import BaseLogger, GuildLogger

def basic_context(user_id: int,
                  logger: BaseLogger,
                  permissions: Permissions = None,
                  on_flush: callable = None) -> ExecutionContext:
    return ExecutionContext(user_id=user_id,
                            logger=logger,
                            permissions=permissions,
                            on_flush=on_flush)

def discord_context(interaction: Interaction) -> ExecutionContext:
    return basic_context(user_id=interaction.user.id,
                         logger=GuildLogger(interaction.guild_id),
                         permissions=PermissionProvider().evaluate_permissions_for_user(interaction.guild_id, interaction.user.id),
                         on_flush=lambda message, exc: GuildLogger(interaction.guild_id).respond(interaction, message))