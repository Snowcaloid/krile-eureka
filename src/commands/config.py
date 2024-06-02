import bot
import data.cache.message_cache as cache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Embed, Interaction, Role
from discord.channel import TextChannel
from data.eureka_info import EurekaTrackerZone
from data.events.event import Event, EventCategory
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_message_functions import GuildMessageFunction
from data.guilds.guild_role_functions import GuildRoleFunction
from data.validation.input_validator import InputValidator
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message


class ConfigCommands(GroupCog, group_name='config', group_description='Config commands.'):
    @command(name = "create_schedule_post", description = "Initialize the server\'s schedule by creating a static post that will be used as an event list.")
    @check(PermissionValidator.is_admin)
    async def create_schedule_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        guild_data = bot.instance.data.guilds.get(interaction.guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.SCHEDULE_POST)
        if message_data:
            old_channel = bot.instance.get_channel(message_data.channel_id)
            if old_channel:
                old_message = await cache.messages.get(message_data.message_id, old_channel)
                if old_message:
                    await old_message.delete()
            guild_data.messages.remove(message_data.message_id) # TODO: This routine is used multiple times. It could be moved somewhere else
        message = await channel.send(embed=Embed(description='...'))
        guild_data.messages.add(message.id, channel.id, GuildMessageFunction.SCHEDULE_POST)
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        await default_response(interaction, f'Schedule has been created in #{channel.name}')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has created a schedule post in #{channel.name}.')

    @command(name = "create_eureka_info_post", description = "Create an updated eureka post for a guild.")
    @check(PermissionValidator.is_admin)
    async def create_eureka_info_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        guild_data = bot.instance.data.guilds.get(interaction.guild_id)
        message_data = guild_data.messages.get(GuildMessageFunction.EUREKA_INFO)
        if message_data:
            await bot.instance.data.ui.eureka_info.remove(interaction.guild_id)
            guild_data.messages.remove(message_data.message_id)
        message = await channel.send(embed=Embed(description='_ _'))
        guild_data.messages.add(message.id, channel.id, GuildMessageFunction.EUREKA_INFO)
        await bot.instance.data.ui.eureka_info.create(interaction.guild_id)
        await default_response(interaction, f'Eureka Info Post has been created in #{channel.name}')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has created a eureka info post in #{channel.name}.')

    async def config_channel(self, interaction: Interaction, event_type: str, channel: TextChannel,
                             function: GuildChannelFunction, function_desc: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        channels_data = bot.instance.data.guilds.get(interaction.guild_id).channels
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            channels_data.set(channel.id, function, event_type)
            desc = Event.by_type(event_type).short_description()
        else:
            channels_data.set_category(channel.id, function, EventCategory(event_type))
            desc = EventCategory(event_type).value
        await default_response(interaction, f'You have set #{channel.name} as the {function_desc} channel for type "{desc}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has set #{channel.name} as the {function_desc} channel for type "{desc}".')

    @command(name = "passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted.")
    @check(PermissionValidator.is_admin)
    async def passcode_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.PASSCODES, 'main passcode')

    @command(name = "support_passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted (for support parties).")
    @check(PermissionValidator.is_admin)
    async def support_passcode_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.SUPPORT_PASSCODES, 'support passcode')

    @command(name = "party_leader_channel", description = "Set the channel for party leader posts.")
    @check(PermissionValidator.is_admin)
    async def party_leader_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.PL_CHANNEL, 'party leader recruitment')

    @command(name = "notification_channel", description = "Set the channel for run schedule notifications.")
    @check(PermissionValidator.is_admin)
    async def notification_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.RUN_NOTIFICATION, 'run notification')

    @command(name = "eureka_notification_channel", description = "Set the channel for eureka tracker notifications.")
    @check(PermissionValidator.is_admin)
    async def eureka_notification_channel(self, interaction: Interaction, instance: str, channel: TextChannel):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_eureka_instance(interaction, instance): return
        channels_data = bot.instance.data.guilds.get(interaction.guild_id).channels
        channels_data.set(channel.id, GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION, instance)
        await default_response(interaction, f'You have set #{channel.name} as the eureka tracker notification channel for "{EurekaTrackerZone(int(instance)).name}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has set #{channel.name} as the eureka tracker notification channel for type "{EurekaTrackerZone(int(instance)).name}".')

    @command(name = "missed_run_channel", description = "Create a missed run list.")
    @check(PermissionValidator.is_admin)
    async def missed_run_channel(self, interaction: Interaction, event_category: str, channel: TextChannel):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_category(interaction, event_category): return
        channels_data = bot.instance.data.guilds.get(interaction.guild_id).channels
        channels_data.set(channel.id, GuildChannelFunction.MISSED_POST_CHANNEL, event_category)
        await bot.instance.data.ui.missed_runs_list.create(interaction.guild_id, event_category)
        await default_response(interaction, f'You have set #{channel.name} as the missed post channel for category "{EventCategory(event_category).value}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has set #{channel.name} as the missed post channel for category "{EventCategory(event_category).value}".')

    @command(name = "missed_runs_allow_role", description = "Allow a role to react to missed posts.")
    @check(PermissionValidator.is_admin)
    async def missed_runs_allow_role(self, interaction: Interaction, role: Role, event_category: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_category(interaction, event_category): return
        role_data = bot.instance.data.guilds.get(interaction.guild_id).roles
        role_data.add(role.id, GuildRoleFunction.ALLOW_MISSED_RUN_APPLICATION, event_category)
        await default_response(interaction, f'You have added #{role.mention} as allowed role for missed run posts for category "{EventCategory(event_category).value}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has added #{role.name} as allowed role for missed run posts for category "{EventCategory(event_category).value}".')

    @command(name = "missed_runs_forbid_role", description = "Forbid a role to react to missed posts.")
    @check(PermissionValidator.is_admin)
    async def missed_runs_forbid_role(self, interaction: Interaction, role: Role, event_category: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_category(interaction, event_category): return
        role_data = bot.instance.data.guilds.get(interaction.guild_id).roles
        role_data.add(role.id, GuildRoleFunction.FORBID_MISSED_RUN_APPLICATION, event_category)
        await default_response(interaction, f'You have added #{role.mention} as forbidden role for missed run posts for category "{EventCategory(event_category).value}".')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has added #{role.name} as forbidden role for missed run posts for category "{EventCategory(event_category).value}".')

    @passcode_channel.autocomplete('event_type')
    @party_leader_channel.autocomplete('event_type')
    @notification_channel.autocomplete('event_type')
    @support_passcode_channel.autocomplete('event_type')
    async def autocomplete_event_type_with_all(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_type_with_categories(current)

    @eureka_notification_channel.autocomplete('instance')
    async def autocomplete_instance(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.eureka_instance(current)

    @missed_run_channel.autocomplete('event_category')
    @missed_runs_allow_role.autocomplete('event_category')
    @missed_runs_forbid_role.autocomplete('event_category')
    async def autocomplete_event_category(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_categories(current)

    #region error-handling
    @create_schedule_post.error
    @passcode_channel.error
    @support_passcode_channel.error
    @party_leader_channel.error
    @notification_channel.error
    @missed_run_channel.error
    @eureka_notification_channel.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion