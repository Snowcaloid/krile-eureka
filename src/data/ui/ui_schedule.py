from datetime import date
from typing import List
from discord import TextChannel
from data.events.event import ScheduledEvent
import data.cache.message_cache as cache
import bot
from utils import set_default_footer

class DateSeparatedScheduleData:
    """Helper class for separating Schedule entries by date."""
    _list: List[ScheduledEvent]
    _date: date

    def __init__(self, date: date) -> None:
        self._date = date
        self._list = []

class UISchedule:
    """Schedule post."""
    def events_per_date(self, event_list: List[ScheduledEvent]) -> List[DateSeparatedScheduleData]:
        """Splits the event list by date."""
        result = []
        entry: DateSeparatedScheduleData = None
        for data in event_list:
            if not entry or entry._date != data.time.date():
                entry = DateSeparatedScheduleData(data.time.date())
                result.append(entry)
            entry._list.append(data)

        return result

    async def rebuild(self, guild_id: int) -> None:
        guild = bot.instance.data.guilds.get(guild_id)
        if guild is None: return
        schedule_post = guild.schedule.schedule_post
        channel: TextChannel = bot.instance.get_channel(schedule_post.channel)
        if channel is None: return
        post = await cache.messages.get(schedule_post.id, channel)
        if post:
            embed = post.embeds[0]
            embed.title = 'Upcoming Runs'
            embed.thumbnail = bot.instance.user.avatar.url
            embed.description = 'Please note times are quoted both in Server Time (ST) and in brackets your Local Time (LT).'
            embed.clear_fields()
            guild.schedule.all.sort(key=lambda e: e.time)
            per_date = self.events_per_date(guild.schedule.all)
            for data in per_date:
                schedule_on_day = ''
                for event in data._list:
                    desc = event.base.schedule_entry_text
                    schedule_on_day = "\n".join([schedule_on_day, desc])
                embed.add_field(name=data._date.strftime("%A, %d %B %Y"), value=schedule_on_day.lstrip("\n"))

            await post.edit(embed=embed)
            await set_default_footer(post)
        else:
            raise Exception(f'UISchedule.rebuild failed: Could not find message with ID {schedule_post.id}')