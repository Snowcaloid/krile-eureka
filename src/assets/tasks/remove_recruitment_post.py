from datetime import datetime
from typing import override

from utils.basic_types import TaskExecutionType
from data.cache.message_cache import MessageCache
from data.guilds.guild_messages import GuildMessages
from tasks.task import TaskTemplate


class Task_RemoveRecruitmentPost(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.REMOVE_RECRUITMENT_POST

    @override
    def description(self, data: dict, timestamp: datetime) -> str:
        return f'Remove Recruitment Post at {timestamp.strftime("%Y-%m %H:%M ST")}'

    @override
    async def execute(self, obj: dict) -> None:
        if obj and obj["guild"] and obj["message_id"]:
            messages = GuildMessages(obj["guild"])
            message_data = messages.get_by_message_id(obj["message_id"])
            if message_data:
                channel = self.bot.get_text_channel(message_data.channel_id)
                if channel:
                    message = await MessageCache().get(message_data.message_id, channel)
                    if message:
                        await message.delete()
                messages.remove(message_data.message_id)


