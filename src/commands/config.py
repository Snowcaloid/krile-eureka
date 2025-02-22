import bot
from data.cache.message_cache import MessageCache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Embed, Interaction, Role
from discord.channel import TextChannel
from basic_types import EurekaTrackerZone, NotoriousMonster
from data.events.event_category import EventCategory
from data.events.event_templates import EventTemplates
from data.generators.autocomplete_generator import AutoCompleteGenerator
from basic_types import GuildChannelFunction
from basic_types import GuildMessageFunction
from basic_types import GuildPingType
from basic_types import GuildRoleFunction
from basic_types import NOTORIOUS_MONSTERS
from data.guilds.guild_channel import GuildChannels
from data.guilds.guild_messages import GuildMessages
from data.guilds.guild_pings import GuildPings
from data.guilds.guild_roles import GuildRoles
from data.validation.input_validator import InputValidator
from utils import default_defer
from data.validation.permission_validator import PermissionValidator
from logger import feedback_and_log, guild_log_message


class ConfigCommands(GroupCog, group_name='config', group_description='Config commands.'):
    from data.ui.ui import UI
    @UI.bind
    def ui(self) -> UI: ...

    @command(name = "create_schedule_post", description = "Initialize the server\'s schedule by creating a static post that will be used as an event list.")
    @check(PermissionValidator().is_admin)
    async def create_schedule_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        messages = GuildMessages(interaction.guild_id)
        message_data = messages.get(GuildMessageFunction.SCHEDULE_POST)
        if message_data:
            old_channel = bot.instance.get_channel(message_data.channel_id)
            if old_channel:
                old_message = await MessageCache().get(message_data.message_id, old_channel)
                if old_message:
                    await old_message.delete()
            messages.remove(message_data.message_id) # TODO: This routine is used multiple times. It could be moved somewhere else
        message = await channel.send(embed=Embed(description='...'))
        messages.add(message.id, channel.id, GuildMessageFunction.SCHEDULE_POST)
        await self.ui.schedule.rebuild(interaction.guild_id)
        await feedback_and_log(interaction, f'created **schedule post** in {channel.jump_url}')

    @command(name = "create_eureka_info_post", description = "Create an updated eureka post for a guild.")
    @check(PermissionValidator().is_admin)
    async def create_eureka_info_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        messages = GuildMessages(interaction.guild_id)
        message_data = messages.get(GuildMessageFunction.EUREKA_INFO)
        if message_data:
            await self.ui.eureka_info.remove(interaction.guild_id)
            messages.remove(message_data.message_id)
        message = await channel.send(embed=Embed(description='_ _'))
        messages.add(message.id, channel.id, GuildMessageFunction.EUREKA_INFO)
        await self.ui.eureka_info.create(interaction.guild_id)
        await feedback_and_log(interaction, f'created a **Persistent Eureka Info Post** in {channel.jump_url}')

    async def config_channel(self, interaction: Interaction, event_type: str, channel: TextChannel,
                             function: GuildChannelFunction, function_desc: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            GuildChannels(interaction.guild_id).set(channel.id, function, event_type)
            desc = EventTemplates(interaction.guild_id).get(event_type).short_description()
        else:
            GuildChannels(interaction.guild_id).set_category(channel.id, function, EventCategory(event_type))
            desc = EventCategory(event_type).value
        await feedback_and_log(interaction, f'set {channel.jump_url} as the **{function_desc} channel** for type "{desc}".')

    @command(name = "passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted.")
    @check(PermissionValidator().is_admin)
    async def passcode_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.PASSCODES, 'main passcode')

    @command(name = "support_passcode_channel", description = "Set the channel, where passcodes for specific type of events will be posted (for support parties).")
    @check(PermissionValidator().is_admin)
    async def support_passcode_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.SUPPORT_PASSCODES, 'support passcode')

    @command(name = "party_leader_channel", description = "Set the channel for party leader posts.")
    @check(PermissionValidator().is_admin)
    async def party_leader_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.PL_CHANNEL, 'party leader recruitment')

    @command(name = "notification_channel", description = "Set the channel for run schedule notifications.")
    @check(PermissionValidator().is_admin)
    async def notification_channel(self, interaction: Interaction, event_type: str, channel: TextChannel):
        await self.config_channel(interaction, event_type, channel, GuildChannelFunction.RUN_NOTIFICATION, 'run notification')

    @command(name = "eureka_notification_channel", description = "Set the channel for eureka tracker notifications.")
    @check(PermissionValidator().is_admin)
    async def eureka_notification_channel(self, interaction: Interaction, instance: str, channel: TextChannel):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_eureka_instance(interaction, instance): return
        GuildChannels(interaction.guild_id).set(channel.id, GuildChannelFunction.EUREKA_TRACKER_NOTIFICATION, instance)
        await feedback_and_log(interaction, f'set {channel.jump_url} as the **eureka tracker notification channel** for "{EurekaTrackerZone(int(instance)).name}".')

    @command(name = "nm_notification_channel", description = "Set the channel for notorious monster notifications.")
    @check(PermissionValidator().is_admin)
    async def nm_notification_channel(self, interaction: Interaction, notorious_monster: str, channel: TextChannel):
        await default_defer(interaction)
        notorious_monster = InputValidator.NORMAL.notorious_monster_name_to_type(notorious_monster)
        if not await InputValidator.RAISING.check_allowed_notorious_monster(interaction, notorious_monster): return
        GuildChannels(interaction.guild_id).set(channel.id, GuildChannelFunction.NM_PINGS, notorious_monster)
        await feedback_and_log(interaction, f'set {channel.jump_url} as the **NM notification channel** for "{NOTORIOUS_MONSTERS[NotoriousMonster(notorious_monster)]}".')

    @command(name = "set_admin", description = "Set the admin role.")
    @check(PermissionValidator().is_admin)
    async def set_admin(self, interaction: Interaction, role: Role):
        await default_defer(interaction)
        GuildRoles(interaction.guild_id).add(role.id, GuildRoleFunction.ADMIN)
        await feedback_and_log(interaction, f'set {role.mention} as **admin** role for **{interaction.guild.name}**.')

    @command(name = "set_developer", description = "Set the developer role.")
    @check(PermissionValidator().is_admin)
    async def set_developer(self, interaction: Interaction, role: Role):
        await default_defer(interaction)
        GuildRoles(interaction.guild_id).add(role.id, GuildRoleFunction.DEVELOPER)
        await feedback_and_log(interaction, f'set {role.mention} as **developer** role for **{interaction.guild.name}**.')

    @command(name = "add_raid_leader_role", description = "Add the Raid Leader role.")
    @check(PermissionValidator().is_admin)
    async def add_raid_leader_role(self, interaction: Interaction, role: Role, event_category: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_category(interaction, event_category): return
        GuildRoles(interaction.guild_id).add(role.id, GuildRoleFunction.RAID_LEADER, event_category)
        await feedback_and_log(interaction, f'added {role.mention} as **raid leader role** for {EventCategory(event_category).value}.')

    @command(name = "remove_raid_leader_role", description = "Remove the Raid Leader role.")
    @check(PermissionValidator().is_admin)
    async def remove_raid_leader_role(self, interaction: Interaction, role: Role, event_category: str):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_category(interaction, event_category): return
        GuildRoles(interaction.guild_id).remove(role.id, GuildRoleFunction.RAID_LEADER, event_category)
        await feedback_and_log(interaction, f'removed {role.mention} from **raid leader roles** for {EventCategory(event_category).value}.')

    @command(name='ping_add_role', description='Add a ping.')
    @check(PermissionValidator().is_admin)
    async def ping_add_role(self, interaction: Interaction, ping_type: int, event_type: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            GuildPings(interaction.guild_id).add_ping(GuildPingType(ping_type), event_type, role.id)
            desc = EventTemplates(interaction.guild_id).get(event_type).short_description()
        else:
            GuildPings(interaction.guild_id).add_ping_category(GuildPingType(ping_type), EventCategory(event_type), role.id)
            desc = EventCategory(event_type).value
        await feedback_and_log(interaction, f'added a ping for role {role.mention} on event <{GuildPingType(ping_type).name}, {desc}>')

    @command(name='ping_remove_role', description='Remove a ping.')
    @check(PermissionValidator().is_admin)
    async def ping_remove_role(self, interaction: Interaction, ping_type: int, event_type: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            GuildPings(interaction.guild_id).remove_ping(GuildPingType(ping_type), event_type, role.id)
            desc = EventTemplates(interaction.guild_id).get(event_type).short_description()
        else:
            GuildPings(interaction.guild_id).remove_ping_category(GuildPingType(ping_type), EventCategory(event_type), role.id)
            desc = EventCategory(event_type).value
        await feedback_and_log(interaction, f'removed a ping for role {role.mention} on event <{GuildPingType(ping_type).name}, {desc}>')

    @command(name='ping_add_eureka_role', description='Add a ping for eureka tracker notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_add_eureka_role(self, interaction: Interaction, instance: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_eureka_instance(interaction, instance): return
        GuildPings(interaction.guild_id).add_ping(GuildPingType.EUREKA_TRACKER_NOTIFICATION, instance, role.id)
        await feedback_and_log(interaction, f'added {role.mention} as a ping for tracker notifications in **{EurekaTrackerZone(int(instance)).name}**.')

    @command(name='ping_remove_eureka_role', description='Remove a ping for eureka tracker notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_remove_eureka_role(self, interaction: Interaction, instance: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_eureka_instance(interaction, instance): return
        GuildPings(interaction.guild_id).remove_ping(GuildPingType.EUREKA_TRACKER_NOTIFICATION, instance, role.id)
        await feedback_and_log(interaction, f'removed {role.mention} from pings for tracker notifications in **{EurekaTrackerZone(int(instance)).name}**.')

    @command(name='ping_add_nm_role', description='Add a ping for notorious monster notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_add_nm_role(self, interaction: Interaction, notorious_monster: str, role: Role):
        await default_defer(interaction)
        notorious_monster = InputValidator.NORMAL.notorious_monster_name_to_type(notorious_monster)
        if not await InputValidator.RAISING.check_allowed_notorious_monster(interaction, notorious_monster): return
        GuildPings(interaction.guild_id).add_ping(GuildPingType.NM_PING, notorious_monster, role.id)
        await feedback_and_log(interaction, f'added a role {role.mention} ping for **{NOTORIOUS_MONSTERS[NotoriousMonster(notorious_monster)]}**.')

    @command(name='ping_remove_nm_role', description='Remove a ping for notorious monster notifications.')
    @check(PermissionValidator().is_admin)
    async def ping_remove_nm_role(self, interaction: Interaction, notorious_monster: str, role: Role):
        await default_defer(interaction)
        notorious_monster = InputValidator.NORMAL.notorious_monster_name_to_type(notorious_monster)
        if not await InputValidator.RAISING.check_allowed_notorious_monster(interaction, notorious_monster): return
        GuildPings(interaction.guild_id).remove_ping(GuildPingType.NM_PING, notorious_monster, role.id)
        await feedback_and_log(interaction,  f'removed role {role.mention} ping for **{NOTORIOUS_MONSTERS[NotoriousMonster(notorious_monster)]}**.')

    @ping_add_role.autocomplete('ping_type')
    @ping_remove_role.autocomplete('ping_type')
    async def autocomplete_ping_type(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().ping_type(current)

    @ping_add_eureka_role.autocomplete('instance')
    @ping_remove_eureka_role.autocomplete('instance')
    async def autocomplete_eureka_instance(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().eureka_instance(current)

    @nm_notification_channel.autocomplete('notorious_monster')
    @ping_add_nm_role.autocomplete('notorious_monster')
    @ping_remove_nm_role.autocomplete('notorious_monster')
    async def autocomplete_eureka_instance(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().notorious_monster(current)

    @passcode_channel.autocomplete('event_type')
    @party_leader_channel.autocomplete('event_type')
    @notification_channel.autocomplete('event_type')
    @support_passcode_channel.autocomplete('event_type')
    @ping_add_role.autocomplete('event_type')
    @ping_remove_role.autocomplete('event_type')
    async def autocomplete_event_type_with_all(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().event_type_with_categories(current, interaction.guild_id)

    @eureka_notification_channel.autocomplete('instance')
    async def autocomplete_instance(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().eureka_instance(current)

    @add_raid_leader_role.autocomplete('event_category')
    @remove_raid_leader_role.autocomplete('event_category')
    async def autocomplete_event_category(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator().event_categories(current)

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
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion