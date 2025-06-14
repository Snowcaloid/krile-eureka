from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import List

from data.events.event_category import EventCategory


@unique
class PermissionLevel(Enum):
    NONE = ''
    VIEW = 'view'
    FULL = 'full'


@dataclass
class ModulePermissions:
    channels: PermissionLevel = field(default=PermissionLevel.NONE)
    roles: PermissionLevel = field(default=PermissionLevel.NONE)
    messages: PermissionLevel = field(default=PermissionLevel.NONE)
    events: PermissionLevel = field(default=PermissionLevel.NONE)
    event_templates: PermissionLevel = field(default=PermissionLevel.NONE)
    signups: PermissionLevel = field(default=PermissionLevel.NONE)
    faq: PermissionLevel = field(default=PermissionLevel.NONE)
    docs: PermissionLevel = field(default=PermissionLevel.NONE)


@dataclass
class EventAdministrationPermissions:
    category: EventCategory
    level: PermissionLevel = field(default=PermissionLevel.NONE)
    event_templates: PermissionLevel = field(default=PermissionLevel.NONE)
    event_secrets: PermissionLevel = field(default=PermissionLevel.NONE)


@dataclass
class Permissions:
    modules: ModulePermissions = field(default_factory=ModulePermissions)
    event_administration: List[EventAdministrationPermissions] = field(default_factory=list)
    is_developer: bool = False
    is_admin: bool = False
    is_owner: bool = False

    def check_modules(self, needed: ModulePermissions) -> None:
        assert needed.channels is None or \
            needed.channels.value <= self.modules.channels.value, \
            "Missing or restricted <channels> module permission."
        assert needed.roles is None or \
            needed.roles.value <= self.modules.roles.value, \
            "Missing or restricted <roles> module permission."
        assert needed.messages is None or \
            needed.messages.value <= self.modules.messages.value, \
            "Missing or restricted <messages> module permission."
        assert needed.events is None or \
            needed.events.value <= self.modules.events.value, \
            "Missing or restricted <events> module permission."
        assert needed.event_templates is None or \
            needed.event_templates.value <= self.modules.event_templates.value, \
            "Missing or restricted <event> module permission templates."
        assert needed.signups is None or \
            needed.signups.value <= self.modules.signups.value, \
            "Missing or restricted <signups> module permission."
        assert needed.faq is None or \
            needed.faq.value <= self.modules.faq.value, \
            "Missing or restricted <FAQ> module permission."
        assert needed.docs is None or \
            needed.docs.value <= self.modules.docs.value, \
            "Missing or restricted <docs> module permission."

    def check_event_administration(self, needed: List[EventAdministrationPermissions]) -> None:
        for needed_perm in needed:
            found = False
            for perm in self.event_administration:
                if perm.category == needed_perm.category:
                    found = True
                    assert needed_perm.level is None or \
                        needed_perm.level.value <= perm.level.value, \
                        f"Missing or restricted <{needed_perm.category.name}> event category administration permission."
                    assert needed_perm.event_templates is None or \
                        needed_perm.event_templates.value <= perm.event_templates.value, \
                        f"Missing or restricted <{needed_perm.category.name}> event templates permission."
                    assert needed_perm.event_secrets is None or \
                        needed_perm.event_secrets.value <= perm.event_secrets.value, \
                        f"Missing or restricted <{needed_perm.category.name}> event secrets permission."
            assert found, f"Event administration permissions for {needed_perm.category.name} not found."

    def full_check(self, needed: Permissions) -> None:
        assert needed.is_owner is None or self.is_owner, "Only the owner can run this command."
        assert needed.is_admin is None or self.is_admin, "Only an admin can run this command."
        assert needed.is_developer is None or self.is_developer, "Only a developer can run this command."
        if needed.modules is not None:
            self.check_modules(needed.modules)
        if needed.event_administration is not None:
            self.check_event_administration(needed.event_administration)

FULL_ACCESS = Permissions(
    modules=ModulePermissions(
        channels=PermissionLevel.FULL,
        roles=PermissionLevel.FULL,
        messages=PermissionLevel.FULL,
        events=PermissionLevel.FULL,
        event_templates=PermissionLevel.FULL,
        signups=PermissionLevel.FULL,
        faq=PermissionLevel.FULL,
        docs=PermissionLevel.FULL
    ),
    event_administration=[
        EventAdministrationPermissions(
            event_category,
            level=PermissionLevel.FULL,
            event_templates=PermissionLevel.FULL,
            event_secrets=PermissionLevel.FULL,
        ) for event_category in EventCategory
    ],
    is_developer=True,
    is_admin=True,
    is_owner=True
)
ADMIN_ACCESS = Permissions(
    modules=ModulePermissions(
        channels=PermissionLevel.FULL,
        roles=PermissionLevel.FULL,
        messages=PermissionLevel.FULL,
        events=PermissionLevel.FULL,
        event_templates=PermissionLevel.FULL,
        signups=PermissionLevel.FULL,
        faq=PermissionLevel.FULL,
        docs=PermissionLevel.FULL
    ),
    event_administration=[
        EventAdministrationPermissions(
            event_category,
            level=PermissionLevel.FULL,
            event_templates=PermissionLevel.FULL,
            event_secrets=PermissionLevel.FULL,
        ) for event_category in EventCategory
    ],
    is_admin=True
)
DEV_ACCESS = Permissions(
    modules=ModulePermissions(
        channels=PermissionLevel.FULL,
        roles=PermissionLevel.FULL,
        messages=PermissionLevel.FULL,
        events=PermissionLevel.FULL,
        event_templates=PermissionLevel.FULL,
        signups=PermissionLevel.FULL,
        faq=PermissionLevel.FULL,
        docs=PermissionLevel.FULL
    ),
    event_administration=[
        EventAdministrationPermissions(
            event_category,
            level=PermissionLevel.FULL,
            event_templates=PermissionLevel.FULL,
            event_secrets=PermissionLevel.FULL,
        ) for event_category in EventCategory
    ],
    is_developer=True
)
NO_ACCESS = Permissions(
    modules=ModulePermissions(
        channels=PermissionLevel.NONE,
        roles=PermissionLevel.NONE,
        messages=PermissionLevel.NONE,
        events=PermissionLevel.NONE,
        event_templates=PermissionLevel.NONE,
        signups=PermissionLevel.NONE,
        faq=PermissionLevel.NONE,
        docs=PermissionLevel.NONE
    ),
    event_administration=[],
    is_developer=False,
    is_admin=False,
    is_owner=False
)