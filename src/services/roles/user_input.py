from typing import override
from services._base.user_input import BaseUserInput
from models.channel import ChannelStruct


class RoleUserInput(BaseUserInput[ChannelStruct]):
    @override
    def validate_and_fix(self, struct: ChannelStruct) -> None:
        ...

    @override
    def can_insert(self, struct: ChannelStruct) -> bool:
        assert struct.role_id is not None, "Role sync insert failure: RoleStruct is missing Role ID"
        assert struct.function is not None, "Role sync insert failure: RoleStruct is missing function"
        return True

    @override
    def can_remove(self, struct: ChannelStruct) -> bool:
        assert struct.role_id is not None, "Role removal failure: RoleStruct is missing Role ID"
        assert struct.function is not None, "Role removal failure: RoleStruct is missing function"
        return True
