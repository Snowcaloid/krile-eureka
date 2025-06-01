from __future__ import annotations
from dataclasses import dataclass
from typing import List, override
from bot import Bot
from centralized_data import GlobalCollection
from data.db.sql import SQL, Record
from data.events.event_category import EventCategory
from data.services.context_service import ServiceContext
from utils.basic_types import GuildChannelFunction, GuildID

class _UserInput:
    @Bot.bind
    def _bot(self) -> Bot: ...

    def __init__(self, struct: ChannelStruct):
        self.struct = struct

    from data.services.validators.eureka_types_service import EurekaTypesService
    @EurekaTypesService.bind
    def _eureka_types_service(self) -> EurekaTypesService: ...

    def validate_and_fix(self) -> None:
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
                from data.services.validators.event_types_service import EventTypesService

                self.struct.event_type = EventTypesService(self.struct.guild_id).event_type_name_to_type(self.struct.event_type)
                assert EventTypesService(self.struct.guild_id).is_event_type_or_category(self.struct.event_type), \
                    f"Invalid event type: {self.struct.event_type}"

@dataclass
class ChannelStruct:
    guild_id: int = None
    id: int = None
    channel_id: int = None
    event_type: str = None
    function: GuildChannelFunction = None

    @Bot.bind
    def _bot(self) -> Bot: ...

    def to_record(self) -> Record:
        record = Record()
        if self.guild_id is not None:
            record['guild_id'] = self.guild_id
        if self.id is not None:
            record['id'] = self.id
        if self.channel_id is not None:
            record['channel_id'] = self.channel_id
        if self.event_type is not None:
            record['event_type'] = self.event_type
        if self.function is not None:
            record['function'] = self.function.value
        return record

    def intersect(self, other: ChannelStruct) -> ChannelStruct:
        return ChannelStruct(
            guild_id=other.guild_id or self.guild_id,
            id=other.id or self.id,
            channel_id=other.channel_id or self.channel_id,
            event_type=other.event_type or self.event_type,
            function=other.function or self.function
        )

    @property
    def user_input(self) -> _UserInput:
        if not hasattr(self, '_user_input'):
            self._user_input = _UserInput(self)
            self._user_input.struct = self
        return self._user_input

    def __eq__(self, other: ChannelStruct) -> bool:
        if other.id and self.id:
            return self.id == other.id
        return (other.guild_id is None or self.guild_id == other.guild_id) and \
            (other.channel_id is None or self.channel_id == other.channel_id) and \
            (other.event_type is None or self.event_type == other.event_type) and \
            (other.function is None or self.function == other.function)

    def __repr__(self) -> str:
        result = []
        if self.guild_id is not None:
            result.append(f"Guild ID: {self.guild_id}")
        if self.id is not None:
            result.append(f"ID: {self.id}")
        if self.channel_id is not None:
            channel_name = self._bot.client.get_channel(self.channel_id).name if self.channel_id else 'Unknown'
            result.append(f"Channel: #{channel_name} ({str(self.channel_id)})")
        if self.event_type is not None:
            result.append(f"Event Type: {self.event_type}")
        if self.function is not None:
            result.append(f"Function: {self.function.name}")
        return ', '.join(result)

    def __reduce__(self, other: ChannelStruct) -> str:
        result = []
        if other.id != self.id:
            result.append(f"ID: {self.id} -> {other.id}")
        if other.channel_id != self.channel_id:
            channel_name = self._bot.client.get_channel(self.channel_id).name if self.channel_id else 'Unknown'
            other_channel_name = self._bot.client.get_channel(other.channel_id).name if other.channel_id else 'Unknown'
            result.append(f"Channel: #{channel_name} ({str(self.channel_id)}) -> #{other_channel_name} ({str(other.channel_id)})")
        if other.event_type != self.event_type:
            result.append(f"Event Type: {self.event_type} -> {other.event_type}")
        if other.function != self.function:
            result.append(f"Function: {self.function.name} -> {other.function.name}")
        if not result:
            return "No changes"

    def marshal(self) -> dict:
        return {
            'guild_id': str(self.guild_id),
            'id': str(self.id),
            'channel': {
                'id': str(self.channel_id),
                'name': self._bot.client.get_channel(self.channel_id).name
            },
            'event_type': self.event_type,
            'function': self.function.name
        }

class ChannelsService(GlobalCollection[GuildID]):
    _list: List[ChannelStruct]

    @Bot.bind
    def bot(self) -> Bot: ...

    @override
    def constructor(self, key: GuildID = None) -> None:
        super().constructor(key)
        self._list = []
        self.load()

    def find(self, channel: ChannelStruct) -> ChannelStruct:
        return next((c for c in self._list if c == channel), None)

    def load(self) -> None:
        self._list.clear()
        if self.key is None: return
        for record in SQL('channels').select(where=f'guild_id={self.key}', all=True):
            channel = ChannelStruct(
                guild_id=self.key,
                id=record["id"],
                channel_id=record["channel_id"],
                event_type=record["event_type"],
                function=GuildChannelFunction(record["function"]) if record["function"] else None)
            self._list.append(channel)

    def sync(self, channel: ChannelStruct,
             context: ServiceContext) -> None:
        with context:
            from data.validation.permission import ModulePermissions, PermissionLevel, Permissions#

            context.assert_permissions(Permissions(modules=ModulePermissions(channels=PermissionLevel.FULL)))
            channel.user_input.validate_and_fix()
            assert channel.guild_id is not None, "Channel sync failure: ChannelStruct is missing Guild ID"
            found_channel = self.find(channel)
            if found_channel:
                edited_channel = found_channel.intersect(channel)
                SQL('channels').update(
                    edited_channel.to_record(),
                    f'id={found_channel.id}')
                context.log(f"[CHANNELS] #{self.bot.client.get_channel(edited_channel.channel_id).name} updated successfully.")
                context.log(f"Changes: ```{edited_channel - found_channel}```")
            else:
                assert channel.channel_id is not None, "Channel sync insert failure: ChannelStruct is missing Channel ID"
                assert channel.function is not None, "Channel sync insert failure: ChannelStruct is missing function"
                SQL('channels').insert(channel.to_record())
                context.log(f"[CHANNELS] #{self.bot.client.get_channel(channel.channel_id).name} added successfully.")
                context.log(f"Channel:```{channel}```")
            self.load()

    def sync_category(self, channel: ChannelStruct,
                      event_category: EventCategory,
                      context: ServiceContext) -> None:
        with context:
            from data.services.validators.event_types_service import EventTypesService
            from data.events.event_templates import EventTemplates

            event_category = EventTypesService(self.key).event_category_name_to_category(event_category)
            assert EventTypesService(self.key).is_event_category(event_category), \
                f"Invalid event category: {event_category}"
            for event_template in EventTemplates(self.key).get_by_categories([event_category]):
                self.sync(channel.intersect(ChannelStruct(event_type=event_template.type())), context)
            context.log(f"Channel category `{event_category.name}` synced for channel: ```{channel}```")

    def remove(self, channel: ChannelStruct,
               context: ServiceContext) -> None:
        with context:
            from data.validation.permission import ModulePermissions, PermissionLevel, Permissions

            context.assert_permissions(Permissions(modules=ModulePermissions(channels=PermissionLevel.FULL)))
            assert channel.guild_id is not None, "Channel removal failure: ChannelStruct is missing Guild ID"
            found_channel = self.find(channel)
            if found_channel:
                SQL('channels').delete(f'id={found_channel.id}')
            else:
                assert channel.channel_id is not None, "Channel removal failure: ChannelStruct is missing Channel ID"
                assert channel.function is not None, "Channel removal failure: ChannelStruct is missing function"
                event_type_part = f"and event_type='{channel.event_type}'" if channel.event_type else ''
                SQL('channels').delete((
                    f'guild_id={channel.guild_id} and channel_id={channel.channel_id} '
                    f'and function={channel.function.value} {event_type_part}'))
            context.log(f"Channel assignment removed successfully: ```{channel}```")
            self.load()

    def remove_category(self, channel: ChannelStruct,
                        event_category: EventCategory,
                        context: ServiceContext) -> None:
        with context:
            from data.services.validators.event_types_service import EventTypesService
            from data.events.event_templates import EventTemplates

            event_category = EventTypesService(self.key).event_category_name_to_category(event_category)
            assert EventTypesService(self.key).is_event_category(event_category), \
                f"Invalid event category: {event_category}"
            for event_template in EventTemplates(self.key).get_by_categories([event_category]):
                self.remove(channel.intersect(ChannelStruct(event_type=event_template.type())), context)
            context.log(f"Channel category `{event_category.name}` removed for channel: ```{channel}```")