import re
import bot
import data.cache.message_cache as cache
from datetime import datetime
from discord import Interaction, Member, TextChannel

from data.eureka_info import EurekaTrackerZone
from data.events.event_category import EventCategory
from data.notorious_monsters import NOTORIOUS_MONSTERS, NotoriousMonster
from logger import feedback_and_log
from data.validation.permission_validator import PermissionValidator


class InputValidator:
    NORMAL: 'InputValidator'
    RAISING: 'InputValidator'

    async def check_for_sql_identifiers(self, interaction: Interaction, text: str) -> bool:
        result = not re.search('(\\s|^)(drop|alter|update|set|create|grant|;)\\s', text, re.IGNORECASE)
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried using text `{text}`, which contains a prohibited SQL word.')
        return result

    def event_type_name_to_type(self, event_type: str, guild_id: int) -> str:
        for event in bot.instance.data.guilds.get(guild_id).event_templates.all:
            if event.description() == event_type:
                return event.type()
        return event_type

    def notorious_monster_name_to_type(self, notorious_monster: str) -> str:
        for nm_type, nm_name in NOTORIOUS_MONSTERS.items():
            if nm_name == notorious_monster:
                return nm_type.value
        return notorious_monster

    def rl_name_to_id(self, interaction: Interaction, raid_leader: str) -> int:
        if raid_leader is None: return None
        if raid_leader.isnumeric():
            return int(raid_leader)
        member = interaction.guild.get_member_named(raid_leader)
        if member:
            return member.id
        raise ValueError(f'Raid leader <{raid_leader}> could not be found.')

    async def check_allowed_notorious_monster(self, interaction: Interaction, notorious_monster: str) -> bool:
        result = notorious_monster in NotoriousMonster._value2member_map_
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried using {notorious_monster}, which does not correlate to a supported Notorious Monster.')
        return result

    async def check_valid_event_type(self, interaction: Interaction, event_type: str) -> bool:
        all_event_types = [event_template.type() for event_template in bot.instance.data.guilds.get(interaction.guild_id).event_templates.all]
        result = event_type in all_event_types
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried using {event_type}, which does not correlate to a type of supported runs.')
        return result

    async def check_valid_event_category(self, interaction: Interaction, event_type: str) -> bool:
        result = event_type.replace('_CATEGORY', '') in EventCategory._value2member_map_
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried using {event_type}, which does not correlate to a supported category.')
        return result

    async def check_valid_event_type_or_category(self, interaction: Interaction, event_type: str) -> bool:
        all_event_types = [event_template.type() for event_template in bot.instance.data.guilds.get(interaction.guild_id).event_templates.all]
        result = event_type in all_event_types or (event_type.endswith('_CATEGORY') and
                                                   event_type.replace('_CATEGORY', '') in EventCategory._value2member_map_)
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried using {event_type}, which does not correlate to a supported category or run type.')
        return result

    async def check_valid_raid_leader(self, interaction: Interaction, member: Member, event_type: str) -> bool:
        allowed_categories = PermissionValidator.get_raid_leader_permissions(member)
        event_template = bot.instance.data.guilds.get(interaction.guild_id).event_templates.get(event_type)
        if event_template is None: return False
        result = event_template.category() in allowed_categories
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'no roles allowing raid leading for "{event_template.short_description()}".')
        return result

    async def check_custom_run_has_description(self, interaction: Interaction, event_type: str, description: str) -> bool:
        result = bot.instance.data.guilds.get(interaction.guild_id).event_templates.get(event_type).category() != EventCategory.CUSTOM or description
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, 'tried booking a custom run without description, but description is mandatory for custom runs.')
        return result

    async def check_run_exists(self, interaction: Interaction, event_id: int) -> bool:
        result = not bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id) is None
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried accessing Event ID <{str(event_id)}>, which does not exist.')
        return result

    async def check_allowed_to_change_run(self, interaction: Interaction, event_id: int) -> bool:
        event = bot.instance.data.guilds.get(interaction.guild_id).schedule.get(event_id)
        result = interaction.user.id == event.users.raid_leader or PermissionValidator.is_admin(interaction)
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried editing Event ID <{str(event_id)}> without permissions.')
        return result

    async def check_message_exists(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = not message is None
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried accessing Message with ID <{str(message_id)}>, which does not exist in {channel.mention}.')
        return result

    async def check_message_contains_an_embed(self, interaction: Interaction, channel: TextChannel, message_id: int) -> bool:
        message = await cache.messages.get(int(message_id), channel)
        result = len(message.embeds) > 0
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried accessing embeds in Message with ID <{str(message_id)}>, which does not contain any embeds.')
        return result

    def escape_event_description(self, description: str) -> str:
        if description is None: return None
        return description.replace("'", "''")

    async def check_valid_eureka_instance(self, interaction: Interaction, instance: str) -> bool:
        result = int(instance) in EurekaTrackerZone._value2member_map_
        if self == InputValidator.RAISING and not result:
            await feedback_and_log(interaction, f'tried inputting eureka instance "{instance}", which does not correlate to a supported eureka instance.')
        return result

    async def check_and_combine_date_and_time(self, interaction: Interaction, date: str, time: str) -> datetime:
        try:
            dt = datetime.strptime(date, "%d-%b-%Y")
        except:
            if self == InputValidator.RAISING:
                await feedback_and_log(interaction, f'tried inputting Date "{date}", which is not in valid format. Valid format is most easily accessed by using autocomplete.')
            return None
        try:
            tm = datetime.strptime(time, "%H:%M")
        except:
            if self == InputValidator.RAISING:
                await feedback_and_log(interaction, f'tried inputting Time "{time}", which is not in valid format. Valid format is most easily accessed by using autocomplete.')
            return None
        dt = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        if dt < datetime.utcnow():
            if self == InputValidator.RAISING:
                await feedback_and_log(interaction, f'tried inputting Date {date} {time}, which is not in future.')
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
                    await feedback_and_log(interaction, f'tried inputting Date "{date}", which is not in valid format. Valid format is most easily accessed by using autocomplete.')
                return None
        if time:
            try:
                tm = datetime.strptime(time, "%H:%M")
            except:
                if self == InputValidator.RAISING:
                    await feedback_and_log(interaction, f'tried inputting Time "{time}", which is not in valid format. Valid format is most easily accessed by using autocomplete.')
                return None
        result = datetime(year=dt.year, month=dt.month, day=dt.day, hour=tm.hour, minute=tm.minute)
        if result < datetime.utcnow():
            if self == InputValidator.RAISING:
                await feedback_and_log(interaction, f'tried inputting Date {result.strftime("%d-%b-%y %H%M")}, which is not in future.')
            return None
        return result

InputValidator.NORMAL = InputValidator()
InputValidator.RAISING = InputValidator()
