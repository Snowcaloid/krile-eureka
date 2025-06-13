from typing import override
from user_input._base import BaseUserInput
from models.channel import ChannelStruct
from utils.basic_types import EurekaTrackerZone, GuildChannelFunction, NotoriousMonsters


class ChannelUserInput(BaseUserInput[ChannelStruct]):
    def validate_and_fix(self, struct: ChannelStruct) -> None:
        if struct.guild_id is not None:
            assert self._bot.client.get_guild(struct.guild_id), \
                f"Invalid guild ID: {struct.guild_id}"
        if struct.channel_id is not None:
            assert self._bot.client.get_channel(struct.channel_id), \
                f"Invalid channel ID: {struct.channel_id}"
        if struct.function is not None:
            assert struct.function in GuildChannelFunction, \
                f"Invalid function: {struct.function}"
        match struct.function:
            case GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION:
                struct.event_type = EurekaTrackerZone.name_to_value_str(struct.event_type)
                assert EurekaTrackerZone.is_eureka_zone(struct.event_type), \
                    f"Invalid eureka zone: {struct.event_type}"
            case GuildChannelFunction.NM_PINGS:
                struct.event_type = NotoriousMonsters.name_to_type_str(struct.event_type)
                assert NotoriousMonsters.is_nm_type(struct.event_type), \
                    f"Invalid NM type: {struct.event_type}"
            case _:
                from services.validators.event_types_service import EventTypesService

                struct.event_type = EventTypesService(struct.guild_id).event_type_name_to_type(struct.event_type)
                assert EventTypesService(struct.guild_id).is_event_type_or_category(struct.event_type), \
                    f"Invalid event type: {struct.event_type}"

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
