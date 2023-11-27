from typing import Type
import bot
import data.cache.message_cache as cache
from datetime import datetime
from discord import Interaction, Member, TextChannel

from data.events.event import Event, EventCategory
from data.ui.buttons import ButtonType
from utils import default_response
from data.validation.permission_validator import PermissionValidator


class InputValidator:
    NORMAL: 'InputValidator'
    RAISING: 'InputValidator'

    async def check_valid_event_type(self, interaction: Interaction, event_type: str) -> bool:
        result = event_type in Event.all_types()
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Type {event_type} does not correlate to a type of supported runs.')
        return result

    async def check_valid_event_category(self, interaction: Interaction, event_type: str) -> bool:
        result = event_type in EventCategory._value2member_map_
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Type {event_type} does not correlate to a supported category.')
        return result

    async def check_valid_event_type_or_category(self, interaction: Interaction, event_type: str) -> bool:
        result = event_type in Event.all_types() or event_type in EventCategory._value2member_map_
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Type {event_type} does not correlate to a supported category or run type.')
        return result

    async def check_valid_raid_leader(self, interaction: Interaction, member: Member, event_type: str) -> bool:
        allow_ba, allow_drs, allow_bozja = PermissionValidator.get_raid_leader_permissions(member)
        event_base = Event.by_type(event_type)
        result = event_base.category() == EventCategory.BA and allow_ba
        result = result or (event_base.category() == EventCategory.DRS and allow_drs)
        result = result or (event_base.category() == EventCategory.BOZJA and allow_bozja)
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'You do not have the required raid leading role to interact with run type "{event_base.short_description()}".')
        return result

    async def check_custom_run_has_description(self, interaction: Interaction, event_type: str, description: str) -> bool:
        result = Event.by_type(event_type).category() != EventCategory.CUSTOM or description
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, 'Description is mandatory for custom runs.')
        return result

    async def check_run_exists(self, interaction: Interaction, event_id: int) -> bool:
        result = not bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id) is None
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Event ID <{str(event_id)}> does not exist.')
        return result

    async def check_allowed_to_change_run(self, interaction: Interaction, event_id: int) -> bool:
        event = bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id)
        result = interaction.user.id == event.users.raid_leader or PermissionValidator.is_admin(interaction)
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'You do not have permissions to change Event ID <{str(event_id)}>.')
        return result

    async def check_message_exists(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = not message is None
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Message with id <{str(message_id)}> does not exist in {channel.mention}.')
        return result

    async def check_message_author_is_self(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = message.author.id == bot.instance.user.id
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Message with id <{str(message_id)}> in {channel.mention} is not sent by {bot.instance.user.mention}.')
        return result

    async def check_message_contains_an_embed(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = len(message.embeds) > 0
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Message with id <{str(message_id)} does not contain any embeds.')
        return result

    async def check_embed_contains_field(self, interaction: Interaction, field_id: int) -> bool:
        result = bot.instance.data.embed_controller.get(interaction.user.id).field_exists(field_id)
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Field #{str(field_id)} doesn\'t exist yet.')
        return result

    async def check_embed_contains_button(self, interaction: Interaction, label: str) -> bool:
        result = bot.instance.data.embed_controller.get(interaction.user.id).button_exists(label)
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Button #{label} doesn\'t exist yet.')
        return result

    async def check_valid_button_type(self, interaction: Interaction, button_type: str) -> bool:
        result = button_type is None or button_type in ButtonType._value2member_map_
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Button type {button_type} doesn\'t exist. Use autocomplete.')
        return result

    async def check_button_position_in_range(self, interaction: Interaction, position: int) -> bool:
        result = position < len(bot.instance.data.embed_controller.get(interaction.user.id))
        if self == InputValidator.RAISING and not result:
            await default_response(interaction, f'Position {str(position)} is out of bounds.')
        return result

    def escape_event_description(self, description: str) -> str:
        if description is None: return None
        return description.replace("'", "''")

    async def check_and_combine_date_and_time(self, interaction: Interaction, date: str, time: str) -> datetime:
        try:
            dt = datetime.strptime(date, "%d-%b-%Y")
        except:
            if self == InputValidator.RAISING:
                await default_response(interaction, f'Date "{date}" is not in valid format. Use autocomplete.')
            return None
        try:
            tm = datetime.strptime(time, "%H:%M")
        except:
            if self == InputValidator.RAISING:
                await default_response(interaction, f'Time "{time}" is not in valid format. Use autocomplete.')
            return None
        dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        if dt < datetime.utcnow():
            if self == InputValidator.RAISING:
                await default_response(interaction, f'Date {date} {time} is not in future. Use autocomplete.')
            return None
        return dt

    async def check_and_combine_date_and_time_change_for_event(self, interaction: Interaction,
                                                               event_id: int, date: str, time: str) -> datetime:
        event = bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id)
        dt = event.time.date()
        tm = event.time.time()
        if date:
            try:
                dt = datetime.strptime(date, "%d-%b-%Y")
            except:
                if self == InputValidator.RAISING:
                    await default_response(interaction, f'Date "{date}" is not in valid format. Use autocomplete.')
                return None
        if time:
            try:
                tm = datetime.strptime(time, "%H:%M")
            except:
                if self == InputValidator.RAISING:
                    await default_response(interaction, f'Time "{time}" is not in valid format. Use autocomplete.')
                return None
        result = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        if result < datetime.utcnow():
            if self == InputValidator.RAISING:
                await default_response(interaction, f'Date {result.strftime("%d-%b-%y %H%M")} is not in future. Use autocomplete.')
            return None
        return result

InputValidator.NORMAL = InputValidator()
InputValidator.RAISING = InputValidator()
