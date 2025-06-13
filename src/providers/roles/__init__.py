
from typing import List, override

from discord import Guild
from providers._base import BaseGuildProvider
from models.roles import RoleStruct


class RolesProvider(BaseGuildProvider[RoleStruct]):
    @override
    def db_table_name(self) -> str:
        return 'roles'

    def find_all(self, role: RoleStruct) -> List[RoleStruct]:
        return [r for r in self._list if r == role]

    def as_discord_mention_string(self, role: RoleStruct) -> str:
        guild = self.bot.client.get_guild(self.key)
        role_structs = RolesProvider(guild.id).find_all(role)
        roles = [
            guild.get_role(role.role_id)
            for role in role_structs
            if role.role_id is not None
        ]
        return ' '.join(role.mention for role in roles if role is not None) if roles else ''