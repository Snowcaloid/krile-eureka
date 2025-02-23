from typing import override

from centralized_data import Singleton
from basic_types import TaskExecutionType
from discord.ext.commands import Bot
from data.cache.message_cache import MessageCache
from data.guilds.guild_messages import GuildMessages
from data.tasks.task import TaskTemplate


class Task_RemoveOldMessage(TaskTemplate):
    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_MESSAGE

    @override
    async def execute(self, obj: object) -> None:
        if obj and obj["guild"] and obj["message_id"]:
            messages = GuildMessages(obj["guild"])
            message_data = messages.get_by_message_id(obj["message_id"])
            if message_data:
                channel = Singleton.get_instance(Bot).get_channel(message_data.channel_id)
                if channel:
                    message = await MessageCache().get(message_data.message_id, channel)
                    if message:
                        await message.delete()
                messages.remove(message_data.message_id)


