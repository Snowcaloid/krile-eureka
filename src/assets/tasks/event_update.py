from typing import override

from data.events.event_templates import EventTemplates
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_pings import GuildPings
from utils.basic_types import GuildChannelFunction, GuildPingType, TaskExecutionType
from data.events.event import Event
from data.tasks.task import TaskTemplate
from utils.discord_types import InteractionLike
from utils.functions import user_display_name
from utils.logger import feedback_and_log


class Task_EventUpdate(TaskTemplate):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from data.ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    from data.ui.ui_recruitment_post import UIRecruitmentPost
    @UIRecruitmentPost.bind
    def ui_recruitment_post(self) -> UIRecruitmentPost: ...

    @override
    def type(self) -> TaskExecutionType: return TaskExecutionType.EVENT_UPDATE

    @override
    def runtime_only(self) -> bool: return True

    def changes_to_string(self, changes: dict, old_event: Event) -> str:
        result = []
        guild_id = old_event.guild_id
        if changes.get("type"):
            result.append((
                f'* Run Type changed from {old_event.template.short_description()} '
                f'to {EventTemplates(guild_id).get(changes["type"]).short_description()}'
            ))
        if changes.get("datetime"):
            result.append(f'* Run Time changed from {old_event.time} ST to {self.time} ST')
        if changes.get("raid_leader"):
            result.append(f'* Raid Leader changed from {user_display_name(guild_id, old_event.users.raid_leader)} to {user_display_name(guild_id, changes["raid_leader"]["id"])}')
        if changes.get("auto_passcode"):
            result.append(f'* Auto Passcode changed from {str(old_event.auto_passcode)} to {str(changes.get("auto_passcode"))}')
        if changes.get("use_support"):
            result.append(f'* Use Support changed from {str(old_event.use_support)} to {str(changes.get("use_support"))}')
        if changes.get("description"):
            result.append(f'* Description changed from "{old_event.real_description}" to "{changes.get("description")}"')
        if not result:
            result.append('No changes.')
        return "\n".join(result)

    @override
    async def execute(self, obj: object) -> None:
        if obj.get("event"):
            event: Event = obj["event"]
            interaction: InteractionLike = obj["interaction"]
            changes: dict = obj.get("changes")
            await self.ui_schedule.rebuild(event.guild_id)
            if event.use_recruitment_posts:
                await self.ui_recruitment_post.create(event.guild_id, event.id)
            notification_channel = GuildChannels(event.guild_id).get(GuildChannelFunction.RUN_NOTIFICATION, event.template.type())
            if notification_channel:
                channel = self.bot.client.guild.get_channel(notification_channel.id)
                mentions = await GuildPings(event.guild_id).get_mention_string(GuildPingType.RUN_NOTIFICATION, event.type)
                await channel.send(f'{mentions} {await event.to_string()} has been scheduled.')
            event.create_tasks()
            if changes and changes.get("type"):
                await self.ui_recruitment_post.remove(event.guild_id, event)
                await self.ui_recruitment_post.create(interaction.guild_id, event.id)
            if changes:
                if changes.get("datetime") or changes.get("auto_passcode") or changes.get("use_support"):
                    event.recreate_tasks()
                changes_info = self.changes_to_string(changes, obj["old_event"])
                await feedback_and_log(interaction, f'adjusted run #{str(event.id)}:\n{changes_info}')
            else:
                event.create_tasks()
                await feedback_and_log(interaction, f'scheduled a {event.type} run #{event.id} for {event.time} with description: <{event.description}>.')


