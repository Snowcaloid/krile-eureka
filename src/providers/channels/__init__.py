from typing import override
from providers._base import BaseGuildProvider
from models.channel import ChannelStruct


class ChannelsProvider(BaseGuildProvider[ChannelStruct]):
    @override
    def db_table_name(self) -> str:
        return 'channels'