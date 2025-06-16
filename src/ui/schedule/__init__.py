from datetime import date
from typing import List
from centralized_data import Bindable
from discord import Embed, Message, TextChannel
from data_providers.event_templates import EventTemplateProvider
from data_providers.events import EventsProvider
from data_providers.message_assignments import MessageAssignmentsProvider
from models.event import EventStruct
from models.event_template import EventTemplateStruct
from models.message_assignment import MessageAssignmentStruct
from utils.basic_types import MessageFunction

class DateSeparatedScheduleData:
    """Helper class for separating Schedule entries by date."""
    def __init__(self, event_date: date) -> None:
        self._date: date = event_date
        self._list: List[EventStruct] = []

class SchedulePost(Bindable):
    """Schedule post."""

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    def _embed(self, guild_id: int) -> Embed:
        embed = Embed(title='Upcoming Runs')
        embed.set_thumbnail(url=self._bot.user.avatar.url) #type: ignore literally untrue..
        description = (
            'Please note times are quoted both in Server Time (ST) and in brackets your Local Time (LT).\n'
            'The runs are free-for-all, no signups. Passcodes are posted 15 minutes prior to the run.\n'
            'Just join via the private party finder in Adventuring Forays tab whenever the passcodes are posted.'
        )
        event_list = EventsProvider().find_all(EventStruct(
            guild_id=guild_id,
            canceled=False,
            finished=False
        ))
        event_list.sort(key=lambda e: e.timestamp)
        per_date = self.events_per_date(event_list)
        if not per_date:
            description = f'{description}\n### There are currently no runs scheduled.'
        else:
            event_templates_provider = EventTemplateProvider()
            for data in per_date:
                schedule_on_day = ''
                for event_struct in data._list:
                    event_template = event_templates_provider.find(EventTemplateStruct(
                        guild_id=guild_id,
                        event_type=event_struct.event_type
                    ))
                    desc = event_template.data.schedule_entry_text(
                        rl=self._bot.get_member(guild_id, event_struct.raid_leader).mention,
                        time=event_struct.timestamp,
                        custom=event_struct.custom_description,
                        disable_support=event_struct.disable_support
                    )
                    schedule_on_day = "\n".join([schedule_on_day, desc])
                description = f'{description}\n{data._date.strftime("### %A, %d %B %Y")}{schedule_on_day}'

        embed.description = description
        return embed

    async def create(self, channel: TextChannel) -> Message:
        return await channel.send(embed=self._embed(channel.guild.id))

    def events_per_date(self, event_list: List[EventStruct]) -> List[DateSeparatedScheduleData]:
        """Splits the event list by date."""
        result = []
        entry = None
        for event_struct in event_list:
            if not entry or entry._date != event_struct.timestamp.date():
                entry = DateSeparatedScheduleData(event_struct.timestamp.date())
                result.append(entry)
            entry._list.append(event_struct)

        return result

    async def rebuild(self, guild_id: int) -> None:
        message_assignment_struct = MessageAssignmentsProvider().find(MessageAssignmentStruct(
            guild_id=guild_id,
            function=MessageFunction.SCHEDULE
        ))
        if message_assignment_struct is None: return
        channel = self._bot.get_text_channel(message_assignment_struct.channel_id)
        if channel is None: return
        message = await channel.fetch_message(message_assignment_struct.message_id)
        if message is None: return
        message = await message.edit(embed=self._embed(guild_id))
        if channel.is_news():
            await message.publish()