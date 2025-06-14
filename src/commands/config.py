from data.cache.message_cache import MessageCache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Embed, Interaction, Role
from discord.channel import TextChannel
from data.events.event_category import EventCategory
from data.events.event_templates import EventTemplates
from models.roles import RoleStruct
from data_providers.context import discord_context
from data_writers.channel_assignments import ChannelAssignmentsWriter
from models.channel_assignment import ChannelAssignmentStruct
from data_writers.roles import RolesWriter
from utils.basic_types import EurekaInstance, RoleFunction, NotoriousMonster
from utils.autocomplete import AutoComplete
from utils.basic_types import GuildChannelFunction, GuildMessageFunction, GuildChannelFunction
from data.guilds.guild_messages import GuildMessages
from utils.functions import default_defer
from data.validation.permission_validator import PermissionValidator


class ConfigCommands(GroupCog, group_name='config', group_description='Config commands.'):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    from ui.ui_schedule import UISchedule
    @UISchedule.bind
    def ui_schedule(self) -> UISchedule: ...

    from ui.ui_eureka_info import UIEurekaInfoPost
    @UIEurekaInfoPost.bind
    def ui_eureka_info(self) -> UIEurekaInfoPost: ...

    from data.validation.user_input import UserInput
    @UserInput.bind
    def user_input(self) -> UserInput: ...

    from data_providers.permissions import PermissionProvider
    @PermissionProvider.bind
    def _permissions_provider(self) -> PermissionProvider: ...

    @command(name = "create_schedule_post", description = "Initialize the server\'s schedule by creating a static post that will be used as an event list.")
    @check(PermissionValidator().is_admin)
    async def create_schedule_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        messages = GuildMessages(interaction.guild_id)
        message_data = messages.get(GuildMessageFunction.SCHEDULE)
        if message_data:
            old_channel = self.bot._client.get_channel(message_data.channel_id)
            if old_channel:
                old_message = await MessageCache().get(message_data.message_id, old_channel)
                if old_message:
                    await old_message.delete()
            messages.remove(message_data.message_id) # TODO: This routine is used multiple times. It could be moved somewhere else
        message = await channel.send(embed=Embed(description='...'))
        messages.add(message.id, channel.id, GuildMessageFunction.SCHEDULE)
        await self.ui_schedule.rebuild(interaction.guild_id)
        await feedback_and_log(interaction, f'created **schedule post** in {channel.jump_url}')

    @command(name = "create_eureka_info_post", description = "Create an updated eureka post for a guild.")
    @check(PermissionValidator().is_admin)
    async def create_eureka_info_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        messages = GuildMessages(interaction.guild_id)
        message_data = messages.get(GuildMessageFunction.EUREKA_INSTANCE_INFO)
        if message_data:
            await self.ui_eureka_info.remove(interaction.guild_id)
            messages.remove(message_data.message_id)
        message = await channel.send(embed=Embed(description='_ _'))
        messages.add(message.id, channel.id, GuildMessageFunction.EUREKA_INSTANCE_INFO)
        await self.ui_eureka_info.create(interaction.guild_id)
        await feedback_and_log(interaction, f'created a **Persistent Eureka Info Post** in {channel.jump_url}') #TODO: undefined method?

    @command(name = "sync_channel_category",
             description = "Assign a channel to have a specific function for an entire event category.")
    async def sync_channel_category(self, interaction: Interaction,
                                    event_category: str,
                                    channel: TextChannel,
                                    function: int):
        await default_defer(interaction)
        ChannelAssignmentsWriter(interaction.guild_id).sync_category( #TODO: undefined method?
            ChannelAssignmentStruct(
                guild_id=interaction.guild_id,
                channel_id=channel.id,
                function=GuildChannelFunction(function)
            ),
            event_category,
            discord_context(interaction)
        )

    @command(name = "sync_channel",
             description = "Assign a channel to have a specific function.")
    async def sync_channel_function(self, interaction: Interaction,
                                    function: int,
                                    event_type: str,
                                    channel: TextChannel):
        await default_defer(interaction)
        ChannelAssignmentsWriter(interaction.guild_id).sync(
            ChannelAssignmentStruct(
                guild_id=interaction.guild_id,
                channel_id=channel.id,
                event_type=event_type,
                function=GuildChannelFunction(function)
            ),
            discord_context(interaction)
        )

    @command(name = "set_admin", description = "Set the admin role.")
    @check(PermissionValidator().is_admin)
    async def set_admin(self, interaction: Interaction, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).sync(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.ADMIN
        ),
            discord_context(interaction)
        )

    @command(name = "set_developer", description = "Set the developer role.")
    @check(PermissionValidator().is_admin)
    async def set_developer(self, interaction: Interaction, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).sync(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.DEVELOPER
        ),
            discord_context(interaction)
        )


    @command(name = "add_raid_leader_role", description = "Add the Raid Leader role.")
    @check(PermissionValidator().is_admin)
    async def add_raid_leader_role(self, interaction: Interaction, role: Role, event_category: str):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).sync(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.RAID_LEADER,
            event_category=event_category
        ),
            discord_context(interaction)
        )

    @command(name = "remove_raid_leader_role", description = "Remove the Raid Leader role.")
    @check(PermissionValidator().is_admin)
    async def remove_raid_leader_role(self, interaction: Interaction, role: Role, event_category: str):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).remove(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.RAID_LEADER,
            event_category=event_category
        ),
            discord_context(interaction)
        )

    @command(name='ping_add_role', description='Add a ping.')
    @check(PermissionValidator().is_admin)
    async def ping_add_role(self, interaction: Interaction, ping_type: int, event_type: str, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).sync(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction(ping_type),
            event_category=event_type
        ),
            discord_context(interaction)
        )

    @command(name='ping_remove_role', description='Remove a ping.')
    @check(PermissionValidator().is_admin)
    async def ping_remove_role(self, interaction: Interaction, ping_type: int, event_type: str, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).remove(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction(ping_type),
            event_category=event_type
        ),
            discord_context(interaction)
        )

    @command(name='ping_add_eureka_role', description='Add a ping for eureka tracker notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_add_eureka_role(self, interaction: Interaction, instance: str, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).sync(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.EUREKA_TRACKER_NOTIFICATION,
            event_category=instance
        ),
            discord_context(interaction)
        )

    @command(name='ping_remove_eureka_role', description='Remove a ping for eureka tracker notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_remove_eureka_role(self, interaction: Interaction, instance: str, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).remove(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.EUREKA_TRACKER_NOTIFICATION,
            event_category=instance
        ),
            discord_context(interaction)
        )

    @command(name='ping_add_nm_role', description='Add a ping for notorious monster notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_add_nm_role(self, interaction: Interaction, notorious_monster: str, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).sync(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.NOTORIOUS_MONSTER_NOTIFICATION,
            event_category=notorious_monster
        ),
            discord_context(interaction)
        )

    @command(name='ping_remove_nm_role', description='Remove a ping for notorious monster notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_remove_nm_role(self, interaction: Interaction, notorious_monster: str, role: Role):
        await default_defer(interaction)
        RolesWriter(interaction.guild_id).remove(RoleStruct(
            guild_id=interaction.guild_id,
            role_id=role.id,
            function=RoleFunction.NOTORIOUS_MONSTER_NOTIFICATION,
            event_category=notorious_monster
        ),
            discord_context(interaction)
        )

    @ping_add_eureka_role.autocomplete('instance')
    @ping_remove_eureka_role.autocomplete('instance')
    async def autocomplete_eureka_tracker_zone(self, interaction: Interaction, current: str):
        return EurekaInstance.autocomplete(current)

    @ping_add_nm_role.autocomplete('notorious_monster')
    @ping_remove_nm_role.autocomplete('notorious_monster')
    async def autocomplete_notorious_monster(self, interaction: Interaction, current: str):
        return NotoriousMonster.autocomplete(current)

    @passcode_channel.autocomplete('event_type')
    @party_leader_channel.autocomplete('event_type')
    @notification_channel.autocomplete('event_type')
    @support_passcode_channel.autocomplete('event_type')
    @ping_add_role.autocomplete('event_type')
    @ping_remove_role.autocomplete('event_type')
    async def autocomplete_event_type_with_all(self, interaction: Interaction, current: str):
        return EventTemplates.autocomplete(current, interaction.guild_id)

    @add_raid_leader_role.autocomplete('event_category')
    @remove_raid_leader_role.autocomplete('event_category')
    async def autocomplete_event_category(self, interaction: Interaction, current: str):
        return EventCategory.autocomplete(current)

    #region error-handling
    @create_schedule_post.error
    @passcode_channel.error
    @support_passcode_channel.error
    @party_leader_channel.error
    @notification_channel.error
    @eureka_notification_channel.error
    @ping_add_role.error
    @ping_remove_role.error
    @ping_add_eureka_role.error
    @ping_remove_eureka_role.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}') #TODO: undefined method? Maybe has to be GuildLogger().log()
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion