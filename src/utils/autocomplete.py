from centralized_data import Bindable
from calendar import month_abbr, monthrange
from datetime import date, timedelta
from typing import List
from discord import Interaction
from discord.app_commands import Choice

from utils.functions import filter_choices_by_current

class AutoComplete(Bindable):
    """Autocompletes for proprietary/discord types."""

    def date(self, current: str) -> List[Choice]:    
        today = date.today()
        result = [
            Choice(name='Today', value=f'{str(today.day)}-{month_abbr[today.month]}-{str(today.year)}'),
            Choice(name='Tomorrow', value=f'{str((today + timedelta(days = 1)).day)}-{month_abbr[today.month]}-{str(today.year)}'),
        ]
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for idx, day_name in enumerate(weekdays):
            # Calculate days until next given weekday
            days_ahead = (idx - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # Always next, not today
            next_day = today + timedelta(days=days_ahead)
            dt = f"{next_day.day}-{month_abbr[next_day.month]}-{next_day.year}"
            result.append(Choice(name=day_name, value=dt))
        
        if len(current) >= 2 and current[0:2].isdigit():  # xx-06-2000
            day = int(current[0:2])
            for i in range(1, 13):
                if monthrange(date.today().year, i)[1] >= day and date.today() <= date(date.today().year, i, day):
                    dt = f'{day}-{month_abbr[i]}-{date.today().year}'
                    result.append(Choice(name=dt, value=dt))
            for i in range(1, 13):
                if monthrange(date.today().year + 1, i)[1] >= day:
                    dt = f'{day}-{month_abbr[i]}-{date.today().year + 1}'
                    result.append(Choice(name=dt, value=dt))
        return filter_choices_by_current(result, current)

    def time(self, current: str) -> List[Choice]:
        result = [Choice(name=f'{str(i).zfill(2)}:00', value=f'{str(i).zfill(2)}:00') for i in range(0, 24)] # round hours

        if len(current) >= 2 and current[0:2].isdigit():
            hour = int(current[0:2])
            if hour < 24 and hour >= 0:
                for i in range(0, 60, 15):
                    dt = f'{str(hour)}:{str(i).zfill(2)}'
                    result.append(Choice(name=dt, value=dt))
        return filter_choices_by_current(result, current)

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