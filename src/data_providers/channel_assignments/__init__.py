from typing import override
from models.channel_assignment import ChannelAssignmentStruct
from data_providers._base import BaseProvider


class ChannelAssignmentProvider(BaseProvider[ChannelAssignmentStruct]):
    @override
    def struct_type(self) -> type[ChannelAssignmentStruct]:
        return ChannelAssignmentStruct