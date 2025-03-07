
from dataclasses import dataclass, field
from typing import List
from centralized_data import GlobalCollection

from api_server.guild_manager import GuildManager
from utils.discord_types import API_Interaction

@dataclass
class Permission:
    @dataclass
    class Guild:
        id: int = 0
        name: str = ''

    @dataclass
    class ModulePermissions:
        events: bool = False
        signups: bool = False
        event_templates: bool = False
        roles: bool = False
        channels: bool = False
        pings: bool = False
        messages: bool = False
        docs: bool = False
        faqs: bool = False

        @property
        def any(self) -> bool:
            return any([
                self.events,
                self.signups,
                self.event_templates,
                self.roles,
                self.channels,
                self.pings,
                self.messages,
                self.docs,
                self.faqs])

    @dataclass
    class Categories:
        admin: bool = False
        raid_leader: bool = False

        @property
        def any(self) -> bool:
            return any([
                self.admin,
                self.raid_leader])

    @dataclass
    class RaidLeading:
        categories: List[str] = field(default_factory=list)

    guild: Guild = field(default_factory=Guild)
    categories: Categories = field(default_factory=Categories)
    modules: ModulePermissions = field(default_factory=ModulePermissions)
    raid_leading: RaidLeading = field(default_factory=RaidLeading)
    apiRequests: bool = False

    @property
    def any(self) -> bool:
        return any([
            self.categories.any,
            self.modules.any,
            self.apiRequests])

class Permissions(List[Permission]):
    def for_guild(self, guild_id: int) -> Permission:
        return next(perm for perm in self if perm.guild.id == guild_id)

class PermissionManager(GlobalCollection[int]):
    from data.validation.permission_validator import PermissionValidator
    @PermissionValidator.bind
    def permission_validator(self) -> PermissionValidator: ...

    def constructor(self, key: int) -> None:
        super().constructor(key)

    def calculate(self) -> Permissions:
        permissions: Permissions = Permissions()
        for guild in GuildManager(self.key).all:
            permission = Permission(guild=Permission.Guild(id=guild.id, name=guild.name))
            self.calculate_categories(permission, guild.id)
            self.calculate_modules(permission, guild.id)
            permission.apiRequests = permission.any
            permissions.append(permission)
        return permissions

    def calculate_categories(self, permission: Permission, guild_id: int) -> None:
        interaction = API_Interaction(self.key, guild_id)
        permission.categories.admin = self.permission_validator.is_admin(interaction)
        permission.categories.raid_leader = self.permission_validator.is_raid_leader(interaction)
        if interaction.user is None: return
        permission.raid_leading.categories = [cat.value for cat in self.permission_validator.get_raid_leader_permissions(interaction.user)]

    def calculate_modules(self, permission: Permission, guild_id: int) -> None:
        self.calculate_rl_modules(permission, guild_id)
        self.calculate_admin_modules(permission, guild_id)

    def calculate_rl_modules(self, permission: Permission, guild_id: int) -> None:
        base = permission.categories.raid_leader
        permission.modules.event_templates = base
        permission.modules.events = base
        permission.modules.signups = base

    def calculate_admin_modules(self, permission: Permission, guild_id: int) -> None:
        base = permission.categories.admin
        permission.modules.roles = base
        permission.modules.channels = base
        permission.modules.pings = base
        permission.modules.messages = base and False #TODO: not implemented
        permission.modules.docs = base and False #TODO: not implemented
        permission.modules.faqs = base and False #TODO: not implemented