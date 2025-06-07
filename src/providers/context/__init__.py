from centralized_data import Bindable
from models.context import ExecutionContext
from discord import Interaction
from models.permissions import Permissions
from utils.logger import BaseLogger, GuildLogger

class ContextProvider(Bindable):
    def basic_context(self,
                      user_id: int,
                      logger: BaseLogger,
                      permissions: Permissions = None) -> ExecutionContext:
        return ExecutionContext(user_id=user_id, logger=logger, permissions=permissions)

    def discord_context(self, interaction: Interaction, permissions: Permissions = None) -> ExecutionContext:
        return self.basic_context(user_id=interaction.user.id,
                                  logger=GuildLogger(interaction.guild_id),
                                  permissions=permissions,
                                  on_flush=lambda message, exc: GuildLogger(interaction.guild_id).respond(interaction, message))