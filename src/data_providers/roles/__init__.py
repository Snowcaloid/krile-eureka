
from typing import override

from data_providers._base import BaseProvider
from models.roles import RoleStruct
from utils.functions import is_null_or_unassigned


class RolesProvider(BaseProvider[RoleStruct]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def struct_type(self) -> type[RoleStruct]:
        return RoleStruct

    def as_discord_mention_string(self, role: RoleStruct) -> str:
        role_structs = self.find_all(role)
        roles = [
            self._bot.get_role(role.guild_id, role.role_id)
            for role in role_structs
            if not is_null_or_unassigned(role.role_id)
        ]
        return ' '.join(role.mention for role in roles if not role is not None) if roles else ''