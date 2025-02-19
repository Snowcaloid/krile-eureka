from typing import override
import bot
from data.cache.message_cache import MessageCache
from data.tasks.task import TaskExecutionType, TaskTemplate


class Task_RemoveOldMessage(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_MESSAGE

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["guild"] and obj["message_id"]:
            message_data = bot.instance.data.guilds.get(obj["guild"]).messages.get_by_message_id(obj["message_id"])
            if message_data:
                channel = bot.instance.get_channel(message_data.channel_id)
                if channel:
                    message = await MessageCache().get(message_data.message_id, channel)
                    if message:
                        await message.delete()
                bot.instance.data.guilds.get(obj["guild"]).messages.remove(message_data.message_id)


