from typing import override
from models.channel_assignment import ChannelAssignmentStruct
from data_providers._base import BaseProvider


class ChannelAssignmentProvider(BaseProvider[ChannelAssignmentStruct]):
    @override
    def db_table_name(self) -> str:
        return 'channel_assignments'