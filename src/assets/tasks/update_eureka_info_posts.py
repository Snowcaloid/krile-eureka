from datetime import datetime, timedelta
from typing import override

import bot
from data.eureka_info import EurekaInfo
from data.guilds.guild import Guilds
from data.guilds.guild_message_functions import GuildMessageFunction
from data.tasks.task import TaskExecutionType, TaskTemplate
from data.tasks.tasks import Tasks


class Task_UpdateEurekaInfoPosts(TaskTemplate):
    @Tasks.bind
    def tasks(self) -> Tasks: ...

    @EurekaInfo.bind
    def eureka_info(self) -> EurekaInfo: ...

    @Guilds.bind
    def guilds(self) -> Guilds: ...

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
            for guild in self.guilds.all:
                message_data = guild.messages.get(GuildMessageFunction.EUREKA_INFO)
                if message_data:
                    await bot.instance.data.ui.eureka_info.rebuild(guild.id)
        finally:
            self.tasks.remove_all(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)
            self.tasks.add_task(next_exec, TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)


