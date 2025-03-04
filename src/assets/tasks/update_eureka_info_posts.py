from datetime import datetime, timedelta
from typing import override


from utils.basic_types import TaskExecutionType
from data.tasks.task import TaskTemplate


class Task_UpdateEurekaInfoPosts(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from data.tasks.tasks import Tasks
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    from data.eureka_info import EurekaInfo
    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    from data.ui.ui_eureka_info import UIEurekaInfoPost
    @UIEurekaInfoPost.bind
    def ui_eureka_info(self) -> UIEurekaInfoPost: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.UPDATE_EUREKA_INFO_POSTS

    @override
    async def handle_exception(self, e: Exception, obj: object) -> None:
        self.tasks.remove_all(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)
        self.tasks.add_task(datetime.utcnow() + timedelta(minutes=1), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)

    @override
    def runtime_only(self) -> bool: return True

    @override
    async def execute(self, obj: object) -> None:
        next_exec = datetime.utcnow() + timedelta(minutes=1)
        try:
            self.eureka_info.remove_old()
            for guild in self.bot.client.guilds:
                await self.ui_eureka_info.rebuild(guild.id)
        finally:
            self.tasks.remove_all(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)
            self.tasks.add_task(next_exec, TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)


