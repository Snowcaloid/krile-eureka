from typing import override
from services._base.user_input import BaseUserInput
from models.channel import ChannelStruct
from utils.basic_types import GuildChannelFunction


class ChannelUserInput(BaseUserInput[ChannelStruct]):
    from services.validators.eureka_types_service import EurekaTypesService
    @EurekaTypesService.bind
    def _eureka_types_service(self) -> EurekaTypesService: ...

    @override
    def validate_and_fix(self, struct: ChannelStruct) -> None:
        if self.struct.guild_id is not None:
            assert self._bot.client.get_guild(self.struct.guild_id), \
                f"Invalid guild ID: {self.struct.guild_id}"
        if self.struct.channel_id is not None:
            assert self._bot.client.get_channel(self.struct.channel_id), \
                f"Invalid channel ID: {self.struct.channel_id}"
        if self.struct.function is not None:
            assert self.struct.function in GuildChannelFunction, \
                f"Invalid function: {self.struct.function}"
        match self.struct.function:
            case GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION:
                self.struct.event_type = self._eureka_types_service.eureka_zone_name_to_value_str(self.struct.event_type)
                assert self._eureka_types_service.is_eureka_zone(self.struct.event_type), \
                    f"Invalid eureka zone: {self.struct.event_type}"
            case GuildChannelFunction.NM_PINGS:
                self.struct.event_type = self._eureka_types_service.nm_name_to_nm_type_str(self.struct.event_type)
                assert self._eureka_types_service.is_nm_type(self.struct.event_type), \
                    f"Invalid NM type: {self.struct.event_type}"
            case _:
                from services.validators.event_types_service import EventTypesService

                self.struct.event_type = EventTypesService(self.struct.guild_id).event_type_name_to_type(self.struct.event_type)
                assert EventTypesService(self.struct.guild_id).is_event_type_or_category(self.struct.event_type), \
                    f"Invalid event type: {self.struct.event_type}"

    @override
    def can_insert(self, struct: ChannelStruct) -> bool:
        assert struct.channel_id is not None, "Channel sync insert failure: ChannelStruct is missing Channel ID"
        assert struct.function is not None, "Channel sync insert failure: ChannelStruct is missing function"
        return True

    @override
    def can_remove(self, struct: ChannelStruct) -> bool:
        assert struct.channel_id is not None, "Channel removal failure: ChannelStruct is missing Channel ID"
        assert struct.function is not None, "Channel removal failure: ChannelStruct is missing function"
        return True
