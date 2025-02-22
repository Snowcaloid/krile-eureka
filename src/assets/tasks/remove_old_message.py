from typing import override
from basic_types import TaskExecutionType
import bot
from data.cache.message_cache import MessageCache
from data.tasks.task import TaskTemplate


class Task_RemoveOldMessage(TaskTemplate):
    from data.guilds.guild import Guilds
    @Guilds.bind
    def guilds(self) -> Guilds: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_MESSAGE

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["guild"] and obj["message_id"]:
            message_data = self.guilds.get(obj["guild"]).messages.get_by_message_id(obj["message_id"])
            if message_data:
                channel = bot.instance.get_channel(message_data.channel_id)
                if channel:
                    message = await MessageCache().get(message_data.message_id, channel)
                    if message:
                        await message.delete()
                self.guilds.get(obj["guild"]).messages.remove(message_data.message_id)


