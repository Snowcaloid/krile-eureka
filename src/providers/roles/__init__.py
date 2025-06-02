
from typing import List, override
from providers._base import BaseGuildProvider
from models.roles import RoleStruct


class RolesProvider(BaseGuildProvider[RoleStruct]):
    @override
    def db_table_name(self) -> str:
        return 'roles'

    def find_all(self, role: RoleStruct) -> List[RoleStruct]:
        return [r for r in self._list if r == role]