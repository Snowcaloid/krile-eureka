from __future__ import annotations
from typing import override

from discord import TextChannel
from data.db.sql import SQL
from providers.channels import ChannelsProvider
from models.channel import ChannelStruct
from models.context import ExecutionContext
from services._base import BaseService

#TODO: add concept for using a category instead of having a category be a for loop for all event types.
#that likely needs new database fields
class ChannelsService(BaseService[ChannelStruct]):
    from services.channels.user_input import ChannelUserInput
    @ChannelUserInput.bind
    def _user_input(self) -> ChannelUserInput: ...

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def sync(self, channel: ChannelStruct,
             context: ExecutionContext) -> None:
        with context:
            from models.permissions import ModulePermissions, PermissionLevel, Permissions
            context.assert_permissions(Permissions(modules=ModulePermissions(channels=PermissionLevel.FULL)))
            self._user_input.validate_and_fix(channel)
            assert channel.guild_id is not None, "Channel sync failure: ChannelStruct is missing Guild ID"
            found_channel = ChannelsProvider().find(channel)
            if found_channel:
                edited_channel = found_channel.intersect(channel)
                SQL('channels').update(
                    edited_channel.to_record(),
                    f'id={found_channel.id}')
                discord_channel = self._bot.client.get_channel(edited_channel.channel_id)
                assert isinstance(discord_channel, TextChannel), f'Channel sync failure: Wrong channel type: {discord_channel.__class__.__name__}'
                context.log(f"[CHANNELS] #{discord_channel.name} updated successfully.")
                context.log(f"Changes: ```{edited_channel.changes_since(found_channel)}```")
            elif self._user_input.can_insert(channel):
                SQL('channels').insert(channel.to_record())
                discord_channel = self._bot.client.get_channel(channel.channel_id)
                assert isinstance(discord_channel, TextChannel), f'Channel sync failure: Wrong channel type: {discord_channel.__class__.__name__}'
                context.log(f"[CHANNELS] #{discord_channel.name} added successfully.")
                context.log(f"Channel:```{channel}```")

    # def sync_category(self, channel: ChannelStruct,
    #                   event_category: EventCategory,
    #                   context: ExecutionContext) -> None:
    #     with context:
    #         from services.validators.event_types_service import EventTypesService
    #         from data.events.event_templates import EventTemplates

    #         event_category = EventTypesService(channel.guild_id).event_category_name_to_category(event_category)
    #         assert EventTypesService(channel.guild_id).is_event_category(event_category), \
    #             f"Invalid event category: {event_category}"
    #         for event_template in EventTemplates(channel.guild_id).get_by_categories([event_category]):
    #             self.sync(channel.intersect(ChannelStruct(event_type=event_template.type())), context)
    #         context.log(f"Channel category `{event_category.name}` synced for channel: ```{channel}```")

    @override
    def remove(self, channel: ChannelStruct,
               context: ExecutionContext) -> None:
        with context:
            from models.permissions import ModulePermissions, PermissionLevel, Permissions

            context.assert_permissions(Permissions(modules=ModulePermissions(channels=PermissionLevel.FULL)))
            assert channel.guild_id is not None, "Channel removal failure: ChannelStruct is missing Guild ID"
            found_channel = ChannelsProvider().find(channel)
            if found_channel:
                SQL('channels').delete(f'id={found_channel.id}')
            elif self._user_input.can_remove(channel):
                event_type_part = f"and event_type='{channel.event_type}'" if channel.event_type else ''
                SQL('channels').delete((
                    f'guild_id={channel.guild_id} and channel_id={channel.channel_id} '
                    f'and function={channel.function.value} {event_type_part}'))
            context.log(f"Channel assignment removed successfully: ```{channel}```")

    # def remove_category(self, channel: ChannelStruct,
    #                     event_category: Union[EventCategory, str],
    #                     context: ExecutionContext) -> None:
    #     with context:
    #         from services.validators.event_types_service import EventTypesService
    #         from data.events.event_templates import EventTemplates

    #         event_category = EventTypesService(channel.guild_id).event_category_name_to_category(event_category)
    #         assert EventCategory.is_event_category(event_category), \
    #             f"Invalid event category: {event_category}"
    #         for event_template in EventTemplates(channel.guild_id).get_by_categories([event_category]):
    #             self.remove(channel.intersect(ChannelStruct(event_type=event_template.type())), context)
    #         context.log(f"Channel category `{event_category.name}` removed for channel: ```{channel}```")