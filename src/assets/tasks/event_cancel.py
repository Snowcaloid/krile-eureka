from typing import override

from data.events.event import Event
from utils.basic_types import TaskExecutionType
from tasks.task import TaskTemplate
from utils.discord_types import InteractionLike
from utils.logger import feedback_and_log


class Task_EventCancel(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    from ui.ui_recruitment_post import UIRecruitmentPost
    @UIRecruitmentPost.bind
    def ui_recruitment_post(self) -> UIRecruitmentPost: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.EVENT_CANCEL

    @override
    def runtime_only(self) -> bool: return True

    @override
    async def execute(self, obj: object) -> None:
        if obj.get("event"):
            event: Event = obj["event"]
            interaction: InteractionLike = obj["interaction"]
            await self.ui_recruitment_post.remove(obj["guild"], event)
            await self.ui_schedule.rebuild(obj["guild"])
            await feedback_and_log(interaction, f'canceled the run #{event.id}.')


