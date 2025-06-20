
from typing import override

from data_providers._base import BaseProvider
from models.event_template import EventTemplateStruct
from models.roles import RoleStruct
from utils.basic_types import RoleDenominator
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

    def find_by_event_template(self, event_template: EventTemplateStruct, role: RoleStruct) -> RoleStruct:
        assert not is_null_or_unassigned(event_template.guild_id), 'guild ID is required when finding event by event template.'
        assert not is_null_or_unassigned(event_template.event_type), 'event type is required when finding event by event template.'
        role_struct = self.find(role.intersect(RoleStruct(
            guild_id=event_template.guild_id,
            denominator=RoleDenominator.EVENT_TYPE,
            event_type=event_template.event_type
        )))
        if role_struct: return role_struct
        return self.find(role.intersect(RoleStruct(
            guild_id=event_template.guild_id,
            denominator=RoleDenominator.EVENT_CATEGORY,
            event_category=event_template.data.category #TODO: EventCategory for RoleStruct
        )))