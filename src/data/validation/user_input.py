from __future__ import annotations
import re
from datetime import datetime
from centralized_data import Bindable
from discord import Interaction, Member, TextChannel

from utils.basic_types import EurekaTrackerZone, NotoriousMonster
from data.events.event_category import EventCategory
from utils.basic_types import NOTORIOUS_MONSTERS
from data.events.event_templates import EventTemplates
from data.events.schedule import Schedule
from utils.discord_types import API_Interaction
from utils.logger import feedback_and_log
from data.validation.permission_validator import PermissionValidator

class _InputChecker(Bindable):
    """
        Synchronous checks for user inputs.
        Methods return True if the check succeeds.
    """
    @PermissionValidator.bind
    def permissions(self) -> PermissionValidator: ...

    def is_notorious_monster(self, notorious_monster: str) -> bool:
        return notorious_monster in NotoriousMonster._value2member_map_

    def is_event_type(self, guild_id: int, event_type: str) -> bool:
        return event_type in [event_template.type() for event_template in EventTemplates(guild_id).all]

    def is_event_category(self, event_type: str) -> bool:
        return event_type.replace('_CATEGORY', '') in EventCategory._value2member_map_

    def is_raid_leader_for(self, guild_id: int, member: Member, event_type: str) -> bool:
        allowed_categories = self.permissions.get_raid_leader_permissions(member)
        event_template = EventTemplates(guild_id).get(event_type)
        if event_template is None: return False
        return event_template.category() in allowed_categories

    def is_not_custom_run_or_hes_description(self, guild_id: int, event_type: str, description: str) -> bool:
        return EventTemplates(guild_id).get(event_type).category() != EventCategory.CUSTOM or description

    def event_exists(self, guild_id: int, event_id: int) -> bool:
        return not Schedule(guild_id).get(event_id) is None

    def can_change_event(self, guild_id: int, user_id: int, event_id: int) -> bool:
        event = Schedule(guild_id).get(event_id)
        interaction = API_Interaction(user_id, guild_id)
        return user_id == event.users.raid_leader or self.permissions.is_admin(interaction)

    def is_eureka_instance(self, instance: str) -> bool:
        return int(instance) in EurekaTrackerZone._value2member_map_

    def event_time(self, dt: datetime) -> bool:
        return dt >= datetime.utcnow()

    def date_string(self, date: str) -> bool:
        try:
            datetime.strptime(date, "%d-%b-%Y")
        except:
            return False
        return True

    def time_string(self, time: str) -> bool:
        try:
            datetime.strptime(time, "%H:%M")
        except:
            return False
        return True

class _InputCorrection(Bindable):
    """
        Synchronous corrections for user inputs.
    """
    def event_type_name_to_type(self, event_type: str, guild_id: int) -> str:
        for event in EventTemplates(guild_id).all:
            if event.description() == event_type:
                return event.type()
        return event_type

    def notorious_monster_name_to_type(self, notorious_monster: str) -> str:
        for nm_type, nm_name in NOTORIOUS_MONSTERS.items():
            if nm_name == notorious_monster:
                return nm_type.value
        return notorious_monster

    def member_name_to_id(self, guild_id: int, member_name: str) -> int:
        if member_name is None: return None
        if member_name.isnumeric():
            return int(member_name)
        member = guild.get_member_named(member_name)
        if member:
            return member.id
        raise ValueError(f'Raid leader <{member_name}> could not be found.')

    def escape_event_description(self, description: str) -> str:
        if description is None: return None
        return description.replace("'", "''")

    def combine_date_and_time(self, date: str, time: str) -> datetime:
        dt = datetime.strptime(date, "%d-%b-%Y")
        tm = datetime.strptime(time, "%H:%M")
        return datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)

    def combine_date_time_change(self, old_datetime: datetime, date: str, time: str) -> datetime:
        dt = old_datetime.date()
        tm = old_datetime.time()
        if date:
            dt = datetime.strptime(date, "%d-%b-%Y")
        if time:
            tm = datetime.strptime(time, "%H:%M")
        return datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)

class _FailRaiser(Bindable):
    """
        Asynchronous checks with feedback and logging.
        Functions return True if the test fails.
    """
    from data.cache.message_cache import MessageCache
    @MessageCache.bind
    def message_cache(self) -> MessageCache: ...

    @_InputChecker.bind
    def check(self) -> _InputChecker: ...

    async def sql_identifiers(self, interaction: Interaction, text: str) -> bool:
        result = re.search('(\\s|^)(drop|alter|update|set|create|grant|;)\\s', text, re.IGNORECASE)
        if result:
            await feedback_and_log(interaction, f'tried using text `{text}`, which contains a prohibited SQL word.')
        return result

    async def is_not_notorious_monster(self, interaction: Interaction, notorious_monster: str) -> bool:
        result = not self.check.is_notorious_monster(notorious_monster)
        if result:
            await feedback_and_log(interaction, f'tried using {notorious_monster}, which does not correlate to a supported Notorious Monster.')
        return result

    async def is_not_event_type(self, interaction: Interaction, event_type: str) -> bool:
        result = not self.check.is_event_type(interaction.guild_id, event_type)
        if result:
            await feedback_and_log(interaction, f'tried using {event_type}, which does not correlate to a type of supported runs.')
        return result

    async def is_not_event_category(self, interaction: Interaction, event_type: str) -> bool:
        result = not self.check.is_event_category(event_type)
        if result:
            await feedback_and_log(interaction, f'tried using {event_type}, which does not correlate to a supported category.')
        return result

    async def is_not_event_type_or_category(self, interaction: Interaction, event_type: str) -> bool:
        result = not self.check.is_event_type(interaction.guild_id, event_type) and \
            not self.check.is_event_category(event_type)
        if result:
            await feedback_and_log(interaction, f'tried using {event_type}, which does not correlate to a supported category or run type.')
        return result

    async def is_not_raid_leader_for(self, interaction: Interaction, member: Member, event_type: str) -> bool:
        result = not self.check.is_raid_leader_for(interaction.guild_id, member, event_type)
        if result:
            await feedback_and_log(interaction, f'no roles allowing raid leading for "{event_type}".')
        return result

    async def is_custom_run_without_description(self, interaction: Interaction, event_type: str, description: str) -> bool:
        result = not self.check.is_not_custom_run_or_hes_description(interaction.guild_id, event_type, description)
        if result:
            await feedback_and_log(interaction, 'tried booking a custom run without description, but description is mandatory for custom runs.')
        return result

    async def event_does_not_exist(self, interaction: Interaction, event_id: int) -> bool:
        result = not self.check.event_exists(interaction.guild_id, event_id)
        if result:
            await feedback_and_log(interaction, f'tried accessing Event ID <{str(event_id)}>, which does not exist.')
        return result

    async def cant_change_run(self, interaction: Interaction, event_id: int) -> bool:
        result = not self.check.can_change_event(interaction.guild_id, interaction.user.id, event_id)
        if result:
            await feedback_and_log(interaction, f'tried editing Event ID <{str(event_id)}> without permissions.')
        return result

    async def message_not_found(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await self.message_cache.get(int(message_id), channel)
        result = message is None
        if result:
            await feedback_and_log(interaction, f'tried accessing Message with ID <{str(message_id)}>, which does not exist in {channel.mention}.')
        return result

    async def message_doesnt_contain_embeds(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await self.message_cache.get(int(message_id), channel)
        result = len(message.embeds) <= 0
        if result:
            await feedback_and_log(interaction, f'tried accessing embeds in Message with ID <{str(message_id)}>, which does not contain any embeds.')
        return result

    async def is_not_eureka_instance(self, interaction: Interaction, instance: str) -> bool:
        result = not self.check.is_eureka_instance(instance)
        if result:
            await feedback_and_log(interaction, f'tried inputting eureka instance "{instance}", which does not correlate to a supported eureka instance.')
        return result

    async def event_time_in_past(self, interaction: Interaction, dt: datetime) -> bool:
        result = not self.check.event_time(dt)
        if result:
            await feedback_and_log(interaction, f'tried inputting Date {dt.strftime("%d-%b-%y %H%M")}, which is not in future.')
        return result

    async def invalid_date_string_format(self, interaction: Interaction, date: str) -> bool:
        result = not self.check.date_string(date)
        if result:
            await feedback_and_log(interaction, f'tried inputting Date "{date}", which is not in valid format. Valid format is most easily accessed by using autocomplete.')
        return result

    async def invalid_time_string_format(self, interaction: Interaction, time: str) -> bool:
        result = not self.check.time_string(time)
        if result:
            await feedback_and_log(interaction, f'tried inputting Time "{time}", which is not in valid format. Valid format is most easily accessed by using autocomplete.')
        return result

class UserInput(Bindable):
    @_InputChecker.bind
    def check(self) -> _InputChecker: ...

    @_InputCorrection.bind
    def correction(self) -> _InputCorrection: ...

    @_FailRaiser.bind
    def fail(self) -> _FailRaiser: ...
