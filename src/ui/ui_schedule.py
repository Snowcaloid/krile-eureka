from datetime import date
from typing import List
from centralized_data import Bindable
from discord import TextChannel
from data.events.event import Event
from data.cache.message_cache import MessageCache
from utils.basic_types import GuildMessageFunction
from data.events.schedule import Schedule
from data.guilds.guild_messages import GuildMessages

class DateSeparatedScheduleData:
    """Helper class for separating Schedule entries by date."""
    _list: List[Event]
    _date: date

    def __init__(self, date: date) -> None:
        self._date = date
        self._list = []

class UISchedule(Bindable):
    """Schedule post."""

    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    def events_per_date(self, event_list: List[Event]) -> List[DateSeparatedScheduleData]:
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
        message_data = GuildMessages(guild_id).get(GuildMessageFunction.SCHEDULE_POST)
        if message_data is None: return
        channel: TextChannel = self.bot._client.get_channel(message_data.channel_id)
        if channel is None: return
        post = await MessageCache().get(message_data.message_id, channel)
        if post:
            embed = post.embeds[0]
            embed.title = 'Upcoming Runs'
            embed.set_thumbnail(url=self.bot._client.user.avatar.url)
            description = (
                'Please note times are quoted both in Server Time (ST) and in brackets your Local Time (LT).\n'
                'The runs are free-for-all, no signups. Passcodes are posted 15 minutes prior to the run.\n'
                'Just join via the private party finder in Adventuring Forays tab whenever the passcodes are posted.'
            )
            embed.clear_fields()
            Schedule(guild_id).all.sort(key=lambda e: e.time)
            per_date = self.events_per_date(Schedule(guild_id).all)
            if not per_date:
                description = f'{description}\n### There are currently no runs scheduled.'
            else:
                for data in per_date:
                    schedule_on_day = ''
                    for event in data._list:
                        desc = event.schedule_entry_text
                        schedule_on_day = "\n".join([schedule_on_day, desc])
                    description = f'{description}\n{data._date.strftime("### %A, %d %B %Y")}{schedule_on_day}'

            embed.description = description
            message = await post.edit(embed=embed)
            if message.channel.is_news():
                await message.publish()
        else:
            raise Exception(f'UISchedule.rebuild failed: Could not find message with ID {message_data.id}')