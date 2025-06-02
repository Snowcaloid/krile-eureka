from centralized_data import Bindable
from models.context import ServiceContext
from discord import Interaction
from models.permissions import Permissions
from utils.logger import BaseLogger, GuildLogger

class ContextProvider(Bindable):
    def basic_context(self,
                      logger: BaseLogger,
                      permissions: Permissions = None) -> ServiceContext:
        return ServiceContext(logger=logger, permissions=permissions)

    def discord_context(self, interaction: Interaction, permissions: Permissions = None) -> ServiceContext:
        return self.basic_context(logger=GuildLogger(interaction.guild_id),
                                  permissions=permissions,
                                  on_flush=lambda message, exc: GuildLogger(interaction.guild_id).respond(interaction, message))