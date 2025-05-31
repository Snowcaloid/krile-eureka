from __future__ import annotations
from dataclasses import dataclass
from typing import List, override
from bot import Bot
from centralized_data import GlobalCollection
from data.db.sql import SQL, Record
from data.events.event_category import EventCategory
from data.events.event_templates import EventTemplates
from data.services.context_service import ServiceContext
from data.validation.permission import ModulePermissions, PermissionLevel, Permissions
from utils.basic_types import GuildChannelFunction, GuildID

@dataclass
class RoleStruct:
    guild_id: int = None
    id: int = None
    role_id: int = None
    event_type: str = None
    function: GuildChannelFunction = None

    @Bot.bind
    def _bot(self) -> Bot: ...

    def to_record(self) -> Record:
        record = Record()
        if self.guild_id is not None:
            record['guild_id'] = self.guild_id
        if self.id is not None:
            record['id'] = self.id
        if self.role_id is not None:
            record['role_id'] = self.role_id
        if self.event_type is not None:
            record['event_type'] = self.event_type
        if self.function is not None:
            record['function'] = self.function.value
        return record

    def intersect(self, other: RoleStruct) -> RoleStruct:
        return RoleStruct(
            guild_id=other.guild_id or self.guild_id,
            id=other.id or self.id,
            role_id=other.role_id or self.role_id,
            event_type=other.event_type or self.event_type,
            function=other.function or self.function
        )

    def __eq__(self, other: RoleStruct) -> bool:
        if other.id and self.id:
            return self.id == other.id

        return (other.guild_id is None or self.guild_id == other.guild_id) and \
            (other.role_id is None or self.role_id == other.role_id) and \
            (other.event_type is None or self.event_type == other.event_type) and \
            (other.function is None or self.function == other.function)

    def __repr__(self) -> str:
        result = []
        if self.id is not None:
            result.append(f"ID: {self.id}")
        if self.role_id is not None:
            result.append(f"Name: {self._bot.client.get_guild(self.guild_id).get_role(self.role_id).name}")
        if self.event_type is not None:
            result.append(f"Event Type: {self.event_type}")
        if self.function is not None:
            result.append(f"Function: {self.function.name}")
        return ','.join(result)

    def marshal(self) -> dict:
        return {
            'guild_id': str(self.guild_id),
            'id': str(self.id),
            'channel': {
                'id': str(self.role_id),
                'name': self._bot.client.get_channel(self.role_id).name
            },
            'event_type': self.event_type,
            'function': self.function.name
        }

class RolesService(GlobalCollection[GuildID]):
    _list: List[RoleStruct]

    @override
    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    # IMPORTANT: Reading this service must not depend on permissions,
    # it's used by the permissions service itself to determine admin,
    # developer, and raid leader roles.
    def find(self, role: RoleStruct) -> RoleStruct:
        return next((r for r in self._list if r == role), None)

    def find_all(self, role: RoleStruct) -> List[RoleStruct]:
        return [r for r in self._list if r == role]

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('roles').select(where=f'guild_id={self.key}', all=True):
            role = RoleStruct(
                guild_id=self.key,
                id=record["id"],
                role_id=record["role_id"],
                event_type=record["event_type"],
                function=GuildChannelFunction(record["function"]) if record["function"] else None)
            self._list.append(role)

    def sync(self, role: RoleStruct, context: ServiceContext) -> None:
        with context:
            context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
            assert role.guild_id is not None, "Role sync failure: RoleStruct is missing Guild ID"
            found_role = self.find(role)
            if found_role:
                edited_role = found_role.intersect(role)
                SQL('roles').update(
                    edited_role.to_record(),
                    f'id={found_role.id}')
                context.log(f"[ROLES] #{edited_role} updated successfully.")
            else:
                assert role.role_id is not None, "Role sync insert failure: RoleStruct is missing Role ID"
                assert role.function is not None, "Role sync insert failure: RoleStruct is missing function"
                SQL('roles').insert(role.to_record())
                context.log(f"[ROLES] #{role} added successfully.")
            self.load()

    def sync_category(self, channel: RoleStruct, event_category: EventCategory, context: ServiceContext) -> None:
        for event_template in EventTemplates(self.key).get_by_categories([event_category]):
            self.sync(channel.intersect(RoleStruct(event_type=event_template.type())), context)

    def remove(self, role: RoleStruct, context: ServiceContext) -> None:
        with context:
            context.assert_permissions(Permissions(modules=ModulePermissions(roles=PermissionLevel.FULL)))
            assert role.guild_id is not None, "Role removal failure: RoleStruct is missing Guild ID"
            found_role = self.find(role)
            if found_role:
                SQL('roles').delete(f'id={found_role.id}')
                context.log(f"[ROLES] #{found_role} removed successfully.")
            else:
                assert role.role_id is not None, "Role removal failure: RoleStruct is missing Role ID"
                assert role.function is not None, "Role removal failure: RoleStruct is missing function"
                event_type_part = f"and event_type='{role.event_type}'" if role.event_type else ''
                SQL('roles').delete((
                    f'guild_id={role.guild_id} and channel_id={role.role_id} '
                    f'and function={role.function.value} {event_type_part}'))
                context.log(f"[ROLES] #{role} removed successfully.")
            self.load()