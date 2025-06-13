from centralized_data import Bindable
from calendar import month_abbr, monthrange
from datetime import date
from typing import List
from discord import Interaction
from discord.app_commands import Choice

class AutoComplete(Bindable):
    """Autocompletes for proprietary/discord types."""

    #TODO: "today", "tomorrow", "monday", "tuesday", etc.
    #TODO: when date is not specified, show weekdays of the current week.
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

    #TODO: nobody really uses every 5 minutes. Every 15 minutes suffices.
    #TODO: when hour is not specified, show round hours.
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
        current_lower = current.lower()
        assert interaction.guild is not None, "Not a guild interaction"
        for member in interaction.guild.members:
            if current_lower == '' or \
               (member.nick is not None and member.nick.lower().startswith(current_lower)) or \
                   member.name.lower().startswith(current_lower):
                for role in member.roles:
                    if role.permissions.administrator or 'raid lead' in role.name.lower():
                        result.append(Choice(name=member.display_name, value=str(member.id)))
                        break
        return result

    def guild_member(self, interaction: Interaction, current: str) -> List[Choice]:
        users = []
        i = 0
        currentlower = current.lower()
        assert interaction.guild is not None, "Not a guild interaction"
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