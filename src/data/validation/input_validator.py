from time import strftime
from typing import Type
import bot
import data.cache.message_cache as cache
from datetime import datetime
from discord import Interaction, Member, TextChannel

from data.events.event import Event, EventCategory
from utils import default_response
from data.validation.permission_validator import PermissionValidator


class InputValidator:
    NORMAL: Type['InputValidator']
    RAISING: Type['InputValidator']

    @classmethod
    async def check_valid_event_type(cl, interaction: Interaction, event_type: str) -> bool:
        result = event_type in Event.all_types()
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'Type {event_type} does not corelate to a type of supported runs.')
        return result

    @classmethod
    async def check_valid_event_category(cl, interaction: Interaction, event_type: str) -> bool:
        result = event_type in EventCategory._value2member_map_
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'Type {event_type} does not corelate to a supported category.')
        return result

    @classmethod
    async def check_valid_event_type_or_category(cl, interaction: Interaction, event_type: str) -> bool:
        result = event_type in Event.all_types() or event_type in EventCategory._value2member_map_
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'Type {event_type} does not corelate to a supported category or run type.')
        return result

    @classmethod
    async def check_valid_raid_leader(cl, interaction: Interaction, member: Member, event_type: str) -> bool:
        allow_ba, allow_drs, allow_bozja = PermissionValidator.get_raid_leader_permissions(member)
        event_base = Event.by_type(event_type)
        result = event_base.category() == EventCategory.BA and allow_ba
        result = result and event_base.category() == EventCategory.DRS and allow_drs
        result = result and event_base.category() == EventCategory.BOZJA and allow_bozja
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'You do not have the required raid leading role to interact with run type "{event_base.short_description()}".')
        return result

    @classmethod
    async def check_custom_run_has_description(cl, interaction: Interaction, event_type: str, description: str) -> bool:
        result = Event.by_type(event_type).category() == EventCategory.CUSTOM and not description
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, 'Description is mandatory for custom runs.')
        return result

    @classmethod
    async def check_run_exists(cl, interaction: Interaction, event_id: int) -> bool:
        result = not bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id) is None
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'Event ID <{str(event_id)}> does not exist.')
        return result

    @classmethod
    async def check_allowed_to_change_run(cl, interaction: Interaction, event_id: int) -> bool:
        event = bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id)
        result = interaction.user.id == event.users.raid_leader or PermissionValidator.is_admin(interaction)
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'You do not have permissions to change Event ID <{str(event_id)}>.')
        return result

    @classmethod
    async def check_message_exists(cl, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = not message is None
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'Message with id <{str(message_id)} does not exist in {channel.mention}>.')
        return result

    @classmethod
    async def check_message_contains_an_embed(cl, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = message.embeds.count > 0
        if cl == InputValidator.RAISING and not result:
            await default_response(interaction, f'Message with id <{str(message_id)} does not contain any embeds.')
        return result

    @classmethod
    async def check_embed_contains_field(cl, interaction: Interaction, field_id: int) -> bool:
        result = bot.instance.data.embed_controller.get(interaction.user.id).field_exists(id)
        if cl == InputValidator.RAISING and not result:
            return await default_response(interaction, f'Field #{str(field_id)} doesn\'t exist yet.')
        return result

    @classmethod
    async def check_embed_contains_button(cl, interaction: Interaction, label: str) -> bool:
        result = bot.instance.data.embed_controller.get(interaction.user.id).button_exists(id)
        if cl == InputValidator.RAISING and not result:
            return await default_response(interaction, f'Button #{label} doesn\'t exist yet.')
        return result

    @classmethod
    async def check_button_label_changed(cl, interaction: Interaction, old_label: str, new_label: str) -> bool:
        result = old_label != new_label
        if cl == InputValidator.RAISING and not result:
            return await default_response(interaction, f'Button #{old_label} remains unchanged.')
        return result

    @classmethod
    def escape_event_description(cl, description: str) -> str:
        if description is None: return None
        return description.replace("'", "''")

    @classmethod
    async def check_and_combine_date_and_time(cl, interaction: Interaction, date: str, time: str) -> datetime:
        try:
            dt = datetime.strptime(date, "%d-%b-%Y")
        except:
            if cl == InputValidator.RAISING:
                await default_response(interaction, f'Date "{date}" is not in valid format. Use autocomplete.')
            return None
        try:
            tm = datetime.strptime(time, "%H:%M")
        except:
            if cl == InputValidator.RAISING:
                await default_response(interaction, f'Time "{time}" is not in valid format. Use autocomplete.')
            return None
        dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        if dt < datetime.utcnow():
            if cl == InputValidator.RAISING:
                await default_response(interaction, f'Date {date} {time} is not in future. Use autocomplete.')
            return None
        return dt

    @classmethod
    async def check_and_combine_date_and_time_change_for_event(cl, interaction: Interaction,
                                                               event_id: int, date: str, time: str) -> datetime:
        event = bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id)
        dt = event.time.date()
        tm = event.time.time()
        if date:
            try:
                dt = datetime.strptime(date, "%d-%b-%Y")
            except:
                if cl == InputValidator.RAISING:
                    await default_response(interaction, f'Date "{date}" is not in valid format. Use autocomplete.')
                return None
        if time:
            try:
                tm = datetime.strptime(time, "%H:%M")
            except:
                if cl == InputValidator.RAISING:
                    await default_response(interaction, f'Time "{time}" is not in valid format. Use autocomplete.')
                return None
        result = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        if result < datetime.utcnow():
            if cl == InputValidator.RAISING:
                await default_response(interaction, f'Date {strftime("%d-%b-%y %H%M", result)} is not in future. Use autocomplete.')
            return None
        return result

InputValidator.NORMAL = InputValidator()
InputValidator.RAISING = InputValidator()