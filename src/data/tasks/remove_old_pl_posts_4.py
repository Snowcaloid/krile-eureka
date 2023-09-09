import bot
from data.events.event import EventCategory
from data.tasks.tasks import TaskExecutionType, TaskBase


class Task_RemoveOldPLPosts(TaskBase):
    @classmethod
    def type(cl) -> TaskExecutionType: return TaskExecutionType.REMOVE_OLD_PL_POSTS

    @classmethod
    async def execute(cl, obj: object) -> None:
        """Removes Party leader recruitment post."""
        if obj and obj["guild"] and obj["channel"]:
            guild = bot.instance.get_guild(obj["guild"])
            channel = guild.get_channel(obj["channel"])
            messages = [message async for message in channel.history(limit=100)]
            message_list = []
            for message in messages:
                if message.author == bot.instance.user and len(message.content.split('#')) == 2:
                    id = int(message.content.split('#')[1])
                    guild_data = bot.instance.data.guilds.get(guild.id)
                    event = guild_data.schedule.get(id)
                    if event and event.delete_pl_posts and not guild_data.schedule.contains(id):
                        message_list.append(message)
            if message_list:
                await channel.delete_messages(message_list)


