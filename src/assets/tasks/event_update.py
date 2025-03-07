from typing import override

from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from utils.basic_types import GuildChannelFunction, GuildPingType, TaskExecutionType
from data.events.event import Event
from data.tasks.task import TaskTemplate
from utils.discord_types import InteractionLike
from utils.logger import feedback_and_log


class Task_EventUpdate(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from data.ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    from data.ui.ui_recruitment_post import UIRecruitmentPost
    @UIRecruitmentPost.bind
    def ui_recruitment_post(self) -> UIRecruitmentPost: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.EVENT_UPDATE

    @override
    def runtime_only(self) -> bool: return True

    @override
    async def execute(self, obj: object) -> None:
        if obj.get("event"):
            event: Event = obj["event"]
            interaction: InteractionLike = obj["interaction"]
            await self.ui_schedule.rebuild(event.guild_id)
            if event.use_recruitment_posts:
                await self.ui_recruitment_post.create(event.guild_id, event.id)
            notification_channel = GuildChannels(event.guild_id).get(GuildChannelFunction.RUN_NOTIFICATION, event.template.type())
            if notification_channel:
                channel = self.bot.client.guild.get_channel(notification_channel.id)
                mentions = await GuildPings(event.guild_id).get_mention_string(GuildPingType.RUN_NOTIFICATION, event.type)
                await channel.send(f'{mentions} {await event.to_string()} has been scheduled.')
            event.create_tasks()
            await feedback_and_log(interaction, f'scheduled a {event.type} run #{event.id} for {event.time} with description: <{event.description}>.')


