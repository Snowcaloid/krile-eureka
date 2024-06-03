from datetime import datetime, timedelta

import bot
from data.guilds.guild_message_functions import GuildMessageFunction
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_UpdateEurekaInfoPosts(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.UPDATE_EUREKA_INFO_POSTS
    @classmethod
    async def handle_exception(cl, e: Exception, obj: object) -> None:
        bot.instance.data.tasks.remove_all(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)
        bot.instance.data.tasks.add_task(datetime.utcnow() + timedelta(minutes=1), TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)

    @classmethod
    def runtime_only(cl) -> bool: return True

    @classmethod
    async def execute(cl, obj: object) -> None:
        next_exec = datetime.utcnow() + timedelta(minutes=1)
        try:
            bot.instance.data.eureka_info.remove_old()
            for guild in bot.instance.data.guilds.all:
                message_data = guild.messages.get(GuildMessageFunction.EUREKA_INFO)
                if message_data:
                    await bot.instance.data.ui.eureka_info.rebuild(guild.id)
        finally:
            bot.instance.data.tasks.remove_all(TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)
            bot.instance.data.tasks.add_task(next_exec, TaskExecutionType.UPDATE_EUREKA_INFO_POSTS)


