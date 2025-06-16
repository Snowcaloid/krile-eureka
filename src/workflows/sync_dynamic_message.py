

from centralized_data import Bindable
from data_providers.message_assignments import MessageAssignmentsProvider
from data_writers.message_assignments import MessageAssignmentsWriter
from models.context import ExecutionContext
from models.message_assignment import MessageAssignmentStruct
from utils.basic_types import MessageFunction


class SyncDynamicMessageWorkflow(Bindable):
    """Worker for pinging about Eureka-related notorious monster spawns."""

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    from data.cache.message_cache import MessageCache
    @MessageCache.bind
    def _message_cache(self) -> MessageCache: ...

    from ui.schedule import SchedulePost
    @SchedulePost.bind
    def _ui_schedule(self) -> SchedulePost: ...

    from ui.eureka_info import EurekaInfoPost
    @EurekaInfoPost.bind
    def _eureka_info(self) -> EurekaInfoPost: ...

    async def assign(self, function: MessageFunction,
                     channel_id: int,
                     context: ExecutionContext) -> None:
        with context:
            context.log(f'Assigning function {function.name} to channel {channel_id}.')
            message_assignment_struct = MessageAssignmentsProvider().find(MessageAssignmentStruct(
                guild_id=context.guild_id,
                channel_id=channel_id,
                function=function
            ))
            if message_assignment_struct:
                message = await self._message_cache.get(message_assignment_struct.message_id,
                                                        self._bot.get_text_channel(message_assignment_struct.channel_id))
                if message:
                    await message.delete()
            channel = self._bot.get_text_channel(channel_id)
            match function:
                case MessageFunction.EUREKA_INSTANCE_INFO:
                    new_message = await self._eureka_info.create(channel)
                case MessageFunction.SCHEDULE:
                    new_message = await self._ui_schedule.create(channel)
            assert new_message, f'Failed to create message for function {function.name} in channel {channel.name}.'
            MessageAssignmentsWriter().sync(
                MessageAssignmentStruct(
                    guild_id=context.guild_id,
                    channel_id=channel_id,
                    function=function,
                    message_id=new_message.id
                ),
                context
            )



