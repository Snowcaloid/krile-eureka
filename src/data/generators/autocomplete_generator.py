
from calendar import month_abbr, monthrange
from datetime import date
from typing import List
from discord import Interaction
from discord.app_commands import Choice

from data.db.definition import TableDefinitions
from data.eureka_info import EurekaTrackerZone
from data.events.event import EventCategoryCollection, EventCategory

from data.guilds.guild_pings import GuildPingType
from data.guilds.guild_role_functions import GuildRoleFunction
from data.notorious_monsters import NOTORIOUS_MONSTERS
from data.ui.constants import ButtonType
from data.validation.permission_validator import PermissionValidator


class AutoCompleteGenerator:
    @classmethod
    def filter_by_current(cl, list: List[Choice], current: str) -> List[Choice]:
        return [choice for choice in list if choice.name.lower().startswith(current.lower())]

    @classmethod
    def event_type(cl, interaction: Interaction, current: str) -> List[Choice]:
        allow_ba, allow_drs, allow_bozja = PermissionValidator.get_raid_leader_permissions(interaction.user)
        return cl.filter_by_current(EventCategoryCollection.calculate_choices(allow_ba, allow_drs, allow_bozja, True), current)

    @classmethod
    def event_type_with_categories(cl, current: str) -> List[Choice]:
        return cl.filter_by_current(EventCategory.all_category_choices() + [event_base.as_choice() for event_base in EventCategoryCollection.ALL_WITH_CUSTOM], current)

    @classmethod
    def event_categories(cl, current: str) -> List[Choice]:
        return cl.filter_by_current(EventCategory.all_category_choices(), current)

    @classmethod
    def event_categories_short(cl, current: str) -> List[Choice]:
        return cl.filter_by_current(EventCategory.all_category_choices_short(), current)

    @classmethod
    def guild_role_functions(cl, current: str) -> List[Choice]:
        return cl.filter_by_current(GuildRoleFunction.all_function_choices(), current)

    @classmethod
    def notorious_monster(cl, current: str) -> List[Choice]:
        return cl.filter_by_current((Choice(name=nm_name, value=nm_enum.value) for nm_enum, nm_name in NOTORIOUS_MONSTERS.items()), current)

    @classmethod
    def date(cl, current: str) -> List[Choice]:
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

    @classmethod
    def time(cl, current: str) -> List[Choice]:
        result = []
        if len(current) >= 2 and current[0:2].isdigit():
            hour = int(current[0:2])
            if hour < 24 and hour >= 0:
                for i in range(0, 60, 5):
                    dt = f'{str(hour)}:{str(i).zfill(2)}'
                    result.append(Choice(name=dt, value=dt))
        return result

    @classmethod
    def raid_leader(cl, interaction: Interaction, current: str) -> List[Choice]:
        result: List[Choice] = []
        currentlower = current.lower()
        for member in interaction.guild.members:
            if not currentlower or member.nick.lower().startswith(currentlower) or member.name.lower().startswith(currentlower):
                for role in member.roles:
                    if role.permissions.administrator or 'raid lead' in role.name.lower():
                        result.append(Choice(name=member.display_name, value=str(member.id)))
                        break
        return result

    @classmethod
    def guild_member(cl, interaction: Interaction, current: str) -> List[Choice]:
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

    @classmethod
    def ping_type(cl, current: str) -> List[Choice]:
        return cl.filter_by_current([
            Choice(name='Main passcodes',  value=GuildPingType.MAIN_PASSCODE.value),
            Choice(name='Support passcodes', value=GuildPingType.SUPPORT_PASSCODE.value),
            Choice(name='Party leader posts', value=GuildPingType.PL_POST.value),
            Choice(name='Run Notification', value=GuildPingType.RUN_NOTIFICATION.value)
        ], current)

    @classmethod
    def eureka_instance(cl, current: str) -> List[Choice]:
        return cl.filter_by_current([
            Choice(name='Anemos',  value=str(EurekaTrackerZone.ANEMOS.value)),
            Choice(name='Pagos', value=str(EurekaTrackerZone.PAGOS.value)),
            Choice(name='Pyros', value=str(EurekaTrackerZone.PYROS.value)),
            Choice(name='Hydatos', value=str(EurekaTrackerZone.HYDATOS.value))
        ], current)

    @classmethod
    def button_type(cl, current: str) -> List[Choice]:
        return [
            Choice(name='Role selection Button', value=ButtonType.ROLE_SELECTION.value),
            Choice(name='Role display Button', value=ButtonType.ROLE_DISPLAY.value)
        ]

    @classmethod
    def table(cl, current: str) -> List[Choice]:
        return cl.filter_by_current([Choice(name=definition._name, value=definition._name) for definition in TableDefinitions.DEFINITIONS], current)
