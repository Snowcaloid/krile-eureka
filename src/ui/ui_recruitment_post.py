from uuid import uuid4
from centralized_data import Bindable
from discord import ButtonStyle, Embed, Message, TextChannel
from data.events.event import Event
from data.events.schedule import Schedule
from data_providers.context import basic_context
from data_writers.buttons import ButtonsWriter
from models.button import ButtonStruct
from models.button.discord_button import DiscordButton
from models.channel_assignment import ChannelAssignmentStruct
from models.role_assignment import RoleAssignmentStruct
from data_providers.channel_assignments import ChannelAssignmentProvider
from data_providers.role_assignments import RoleAssignmentsProvider
from utils.basic_types import MessageFunction, RoleFunction
from utils.basic_types import EventCategory
from utils.basic_types import ChannelFunction
from ui.base_button import save_buttons
from utils.basic_types import ButtonType
from ui.views import PersistentView
from utils.logger import FileLogger

class UIRecruitmentPost(Bindable):
    """Party leader post."""
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    from data.cache.message_cache import MessageCache
    @MessageCache.bind
    def _message_cache(self) -> MessageCache: ...

    async def create(self, guild_id: int, id: int) -> None:
        event = Schedule(guild_id).get(id)
        if event is None or event.category == EventCategory.CUSTOM or not event.use_recruitment_posts: return
        channel_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
            guild_id=guild_id,
            function=ChannelFunction.RECRUITMENT,
            event_type=event.type
        ))
        if channel_struct is None: return
        channel: TextChannel = self._bot._client.get_channel(channel_struct.channel_id)
        if channel is None: return
        mention_string = RoleAssignmentsProvider().as_discord_mention_string(RoleAssignmentStruct(
            guild_id=guild_id,
            event_type=event.type,
            function=RoleFunction.RECRUITMENT_POST_PING
        ))
        message = await channel.send(mention_string, embed=Embed(description='...'))
        event.recruitment_post = message.id
        message = await self.rebuild(guild_id, id, True)
        GuildMessages(guild_id).add(message.id, channel.id, MessageFunction.RECRUITMENT_POST)
        if event.use_recruitment_post_threads:
            await message.create_thread(name=event.recruitment_post_thread_title)

    async def rebuild(self, guild_id: int, id: int, recreate_view: bool = False) -> Message:
        event = Schedule(guild_id).get(id)
        if event is None or event.category == EventCategory.CUSTOM or not event.use_recruitment_posts: return
        channel_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
            guild_id=guild_id,
            function=ChannelFunction.RECRUITMENT,
            event_type=event.type
        ))
        if channel_struct is None: return
        channel: TextChannel = self._bot._client.get_channel(channel_struct.channel_id)
        message = await self._message_cache.get(event.recruitment_post, channel)
        if message is None: return
        embed = Embed(title=event.recruitment_post_title, description=event.recruitment_post_text)
        if recreate_view:
            ButtonsWriter().remove(
                ButtonStruct(message_id=event.recruitment_post),
                basic_context(0, 0, FileLogger(guild_id)))
            view = PersistentView()
            for i in range(1, 8):
                label = event.pl_button_texts[i-1]
                if label:
                    button = DiscordButton(
                        ButtonType.RECRUITMENT,
                        label=label,
                        custom_id=str(uuid4()),
                        row=1 if i < 4 else 2,
                        index=i - 1 if i < 4 else i - 4,
                        style=ButtonStyle.primary if i < 4 else ButtonStyle.success if i != 7 else ButtonStyle.danger,
                        pl=i-1)
                    button.event_id = event.id
                    view.add_item(button)
            if event.category == EventCategory.BA:
                view.add_item(DiscordButton(
                    ButtonType.SEND_PL_GUIDE,
                    label='How to party lead?',
                    custom_id=str(uuid4()),
                    row=1,
                    index=4,
                    style=ButtonStyle.gray))
            message = await message.edit(embed=embed, view=view)
            save_buttons(message, view)
        else:
            message = await message.edit(embed=embed)
        return message

    async def remove(self, guild_id: int, event: Event) -> None:
        channel_struct = ChannelAssignmentProvider().find(ChannelAssignmentStruct(
            guild_id=guild_id,
            function=ChannelFunction.RECRUITMENT,
            event_type=event.type
        ))
        if channel_struct is None: return
        channel: TextChannel = self._bot._client.get_channel(channel_struct.channel_id)
        message = await self._message_cache.get(event.recruitment_post, channel)
        if message is None: return
        await message.delete()