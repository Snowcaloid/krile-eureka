import bot
import data.cache.message_cache as cache
from data.tasks.tasks import TaskExecutionType, TaskBase

class Task_RemoveMissedRunPost(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.REMOVE_MISSED_RUN_POST

    @classmethod
    async def execute(cl, obj: object) -> None:
        """Removes a missed run post."""
        if obj and obj["guild"] and obj["channel"] and obj["message"]:
            guild = bot.instance.get_guild(obj["guild"])
            if guild is None: return
            channel = guild.get_channel(obj["channel"])
            if channel is None: return
            message = await cache.messages.get(obj["message"], channel)
            if message is None: return
            bot.instance.data.ui.view.delete(message.id)
            await message.delete()


Task_RemoveMissedRunPost.register()
