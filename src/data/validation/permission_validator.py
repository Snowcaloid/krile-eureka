from __future__ import annotations
import os
from typing import List
from centralized_data import Bindable
from discord import Member
from models.role_assignment import RoleAssignmentStruct
from data_providers.role_assignments import RoleAssignmentsProvider
from utils.discord_types import InteractionLike
from utils.basic_types import EventCategory
from utils.basic_types import RoleFunction
from utils.functions import is_null_or_unassigned

class PermissionValidator(Bindable):
    def is_in_guild(self, interaction: InteractionLike) -> bool:
        return not interaction.guild is None

    def is_owner(self, interaction: InteractionLike) -> bool:
        return interaction.user.id == int(os.getenv('OWNER_ID'))

    def is_developer(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_struct = RoleAssignmentsProvider().find(RoleAssignmentStruct(
                function=RoleFunction.DEVELOPER
            ))
            if is_null_or_unassigned(role_struct.role_id): return self.is_owner(interaction)
            return not interaction.user.get_role(role_struct.role_id) is None or self.is_owner(interaction)
        return False

    def is_admin(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_struct = RoleAssignmentsProvider().find(RoleAssignmentStruct(
                function=RoleFunction.ADMIN
            ))
            if is_null_or_unassigned(role_struct.role_id): return self.is_developer(interaction)
            return not interaction.user.get_role(role_struct.role_id) is None or self.is_developer(interaction)
        return False

    def is_raid_leader(self, interaction: InteractionLike) -> bool:
        if self.is_in_guild(interaction):
            role_structs = RoleAssignmentsProvider().find_all(RoleAssignmentStruct(
                function=RoleFunction.RAID_LEADER
            ))
            for role_struct in role_structs:
                if not interaction.user.get_role(role_struct.role_id) is None:
                    return True
            return self.is_admin(interaction)
        return False

    def get_raid_leader_permissions(self, member: Member) -> List[EventCategory]:
        admin_role_struct = RoleAssignmentsProvider().find(RoleAssignmentStruct(
            function=RoleFunction.ADMIN
        ))
        rl_role_structs = RoleAssignmentsProvider().find_all(RoleAssignmentStruct(
            function=RoleFunction.RAID_LEADER
        ))
        categories: List[EventCategory] = []
        for role in member.roles:
            if admin_role_struct and role.id == admin_role_struct.role_id:
                return list(EventCategory)
            else:
                for role_struct in rl_role_structs:
                    if role_struct.role_id == role.id and not role_struct.event_category in categories:
                        categories.append(EventCategory(role_struct.event_category))
        return categories
