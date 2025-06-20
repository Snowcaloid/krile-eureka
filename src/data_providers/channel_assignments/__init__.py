from typing import override
from models.channel_assignment import ChannelAssignmentStruct
from data_providers._base import BaseProvider
from models.event_template import EventTemplateStruct
from utils.basic_types import ChannelDenominator
from utils.functions import is_null_or_unassigned


class ChannelAssignmentProvider(BaseProvider[ChannelAssignmentStruct]):
    @override
    def struct_type(self) -> type[ChannelAssignmentStruct]:
        return ChannelAssignmentStruct

    def find_by_event_template(self, event_template: EventTemplateStruct, channel: ChannelAssignmentStruct) -> ChannelAssignmentStruct:
        assert not is_null_or_unassigned(event_template.guild_id), 'guild ID is required when finding event by event template.'
        assert not is_null_or_unassigned(event_template.event_type), 'event type is required when finding event by event template.'
        channel_struct = self.find(channel.intersect(ChannelAssignmentStruct(
            guild_id=event_template.guild_id,
            denominator=ChannelDenominator.EVENT_TYPE,
            event_type=event_template.event_type
        )))
        if channel_struct: return channel_struct
        return self.find(channel.intersect(ChannelAssignmentStruct(
            guild_id=event_template.guild_id,
            denominator=ChannelDenominator.EVENT_CATEGORY,
            event_category=event_template.data.category
        )))