from typing import override
from models.channel import ChannelStruct
from providers._base import BaseProvider


class ChannelsProvider(BaseProvider[ChannelStruct]):
    @override
    def db_table_name(self) -> str:
        return 'channels'