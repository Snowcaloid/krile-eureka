
from typing import override

from providers._base import BaseProvider
from models.roles import RoleStruct


class RolesProvider(BaseProvider[RoleStruct]):
    @override
    def db_table_name(self) -> str:
        return 'roles'

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def as_discord_mention_string(self, role: RoleStruct) -> str:
        guild = self._bot._client.get_guild(self.key)
        role_structs = self.find_all(role)
        roles = [
            guild.get_role(role.role_id)
            for role in role_structs
            if role.role_id is not None
        ]
        return ' '.join(role.mention for role in roles if role is not None) if roles else ''