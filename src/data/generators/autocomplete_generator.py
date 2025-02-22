from centralized_data import Bindable
import bot
from calendar import month_abbr, monthrange
from datetime import date
from typing import List
from discord import Interaction
from discord.app_commands import Choice

from data.db.definition import TableDefinitions
from basic_types import NOTORIOUS_MONSTERS, EurekaTrackerZone, NotoriousMonster

from data.events.event_category import EventCategory
from basic_types import GuildPingType
from basic_types import GuildRoleFunction
from basic_types import NM_ALIASES
from data.ui.constants import ButtonType
from data.validation.permission_validator import PermissionValidator


class AutoCompleteGenerator(Bindable):
    from data.events.event_templates import EventTemplates
    @EventTemplates.bind
    def event_templates(self) -> EventTemplates: ...

    def filter_by_current(self, list: List[Choice], current: str) -> List[Choice]:
        if current == '':
            return list
        else:
            return [choice for choice in list if choice.name.lower().startswith(current.lower())]

    def event_type(self, interaction: Interaction, current: str) -> List[Choice]:
        allowed_categories = PermissionValidator().get_raid_leader_permissions(interaction.user)
        return self.filter_by_current([
            event_template.as_choice() for event_template in self.event_templates.get_by_categories(interaction.guild_id, allowed_categories)], current)

    def event_type_with_categories(self, current: str, guild_id: int) -> List[Choice]:
        return self.filter_by_current(EventCategory.all_category_choices() + [
            event_template.as_choice() for event_template in self.event_templates.all(guild_id)], current)

    def event_categories(self, current: str) -> List[Choice]:
        return self.filter_by_current(EventCategory.all_category_choices(), current)

    def event_categories_short(self, current: str) -> List[Choice]:
        return self.filter_by_current(EventCategory.all_category_choices_short(), current)

    def guild_role_functions(self, current: str) -> List[Choice]:
        return self.filter_by_current(GuildRoleFunction.all_function_choices(), current)

    def alterantive_nm_names(self, nm_choices: List[Choice], current: str) -> List[Choice]:
        choices: List[Choice] = []
        for choice in nm_choices:
            aliases = NM_ALIASES.get(NotoriousMonster(choice.value), None)
            if aliases:
                for alias in aliases:
                    if alias.lower().startswith(current.lower()):
                        choices.append(Choice(name=alias, value=choice.value))
        return choices

    def notorious_monster(self, current: str) -> List[Choice]:
        nm_choices = [Choice(name=nm_name, value=nm_enum.value) for nm_enum, nm_name in NOTORIOUS_MONSTERS.items()]
        if current:
            return self.filter_by_current(nm_choices, current) + self.alterantive_nm_names(nm_choices, current)
        else:
            return nm_choices

    def date(self, current: str) -> List[Choice]:
        result = []
        if len(current) >= 2 and current[0:2].isdigit():
            day = int(current[0:2])
            for i in range(1, 13):
                if monthrange(date.today().year, i)[1] >= day and date.today() <= date(date.today().year, i, day):
                    dt = f'{str(day)}-{month_abbr[i]}-{str(date.today().year)}'
                    result.append(Choice(name=dt, value=dt))
            for i in range(1, 13):
                if monthrange(date.today().year + 1, i)[1] >= day:
                    dt = f'{str(day)}-{month_abbr[i]}-{str(date.today().year + 1)}'
                    result.append(Choice(name=dt, value=dt))
        return result

    def time(self, current: str) -> List[Choice]:
        result = []
        if len(current) >= 2 and current[0:2].isdigit():
            hour = int(current[0:2])
            if hour < 24 and hour >= 0:
                for i in range(0, 60, 5):
                    dt = f'{str(hour)}:{str(i).zfill(2)}'
                    result.append(Choice(name=dt, value=dt))
        return result

    def raid_leader(self, interaction: Interaction, current: str) -> List[Choice]:
        result: List[Choice] = []
        currentlower = current.lower()
        for member in interaction.guild.members:
            if not currentlower or member.nick.lower().startswith(currentlower) or member.name.lower().startswith(currentlower):
                for role in member.roles:
                    if role.permissions.administrator or 'raid lead' in role.name.lower():
                        result.append(Choice(name=member.display_name, value=str(member.id)))
                        break
        return result

    def guild_member(self, interaction: Interaction, current: str) -> List[Choice]:
        users = []
        i = 0
        currentlower = current.lower()
        for member in interaction.guild.members:
            if member.display_name:
                if member.display_name.lower().startswith(currentlower):
                    users.append(Choice(name=member.display_name, value=str(member.id)))
                    i += 1
            elif member.name.lower().startswith(currentlower):
                users.append(Choice(name=member.name, value=str(member.id)))
                i += 1
            if i == 25:
                break
        return users

    def ping_type(self, current: str) -> List[Choice]:
        return self.filter_by_current([
            Choice(name='Main passcodes',  value=GuildPingType.MAIN_PASSCODE.value),
            Choice(name='Support passcodes', value=GuildPingType.SUPPORT_PASSCODE.value),
            Choice(name='Party leader posts', value=GuildPingType.PL_POST.value),
            Choice(name='Run Notification', value=GuildPingType.RUN_NOTIFICATION.value)
        ], current)

    def eureka_instance(self, current: str) -> List[Choice]:
        return self.filter_by_current([
            Choice(name='Anemos',  value=str(EurekaTrackerZone.ANEMOS.value)),
            Choice(name='Pagos', value=str(EurekaTrackerZone.PAGOS.value)),
            Choice(name='Pyros', value=str(EurekaTrackerZone.PYROS.value)),
            Choice(name='Hydatos', value=str(EurekaTrackerZone.HYDATOS.value))
        ], current)

    def button_type(self, current: str) -> List[Choice]:
        return [
            Choice(name='Role selection Button', value=ButtonType.ROLE_SELECTION.value),
            Choice(name='Role display Button', value=ButtonType.ROLE_DISPLAY.value)
        ]

    def table(self, current: str) -> List[Choice]:
        return self.filter_by_current([Choice(name=definition.name(), value=definition.name()) for definition in TableDefinitions().loaded_assets], current)
