import bot
from discord import Interaction, Role
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from data.eureka_info import EurekaTrackerZone
from data.events.event import Event, EventCategory
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.guilds.guild_pings import GuildPingType
from data.validation.input_validator import InputValidator
from logger import guild_log_message
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator

###################################################################################
# pings
##################################################################################
class PingCommands(GroupCog, group_name='ping', group_description='Commands regarding pinging on certain messages.'):
    @command(name='add_role', description='Add a ping.')
    @check(PermissionValidator.is_admin)
    async def add_role(self, interaction: Interaction, ping_type: int, event_type: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        pings_data = bot.instance.data.guilds.get(interaction.guild_id).pings
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            pings_data.add_ping(GuildPingType(ping_type), event_type, role.id)
            desc = Event.by_type(event_type).short_description()
        else:
            pings_data.add_ping_category(GuildPingType(ping_type), EventCategory(event_type), role.id)
            desc = EventCategory(event_type).value
        feedback = f'added a ping for role **{role.name}** on event <{GuildPingType(ping_type).name}, {desc}>'
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** {feedback}')
        await default_response(interaction, 'You ' + feedback)

    @command(name='remove_role', description='Remove a ping.')
    @check(PermissionValidator.is_admin)
    async def remove_role(self, interaction: Interaction, ping_type: int, event_type: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_event_type_or_category(interaction, event_type): return
        pings_data = bot.instance.data.guilds.get(interaction.guild_id).pings
        if await InputValidator.NORMAL.check_valid_event_type(interaction, event_type):
            pings_data.remove_ping(GuildPingType(ping_type), event_type, role.id)
            desc = Event.by_type(event_type).short_description()
        else:
            pings_data.remove_ping_category(GuildPingType(ping_type), EventCategory(event_type), role.id)
            desc = EventCategory(event_type).value
        feedback = f'removed a ping for role **{role.name}** on event <{GuildPingType(ping_type).name}, {desc}>'
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** {feedback}')
        await default_response(interaction, 'You ' + feedback)

    @command(name='add_eureka_role', description='Add a ping for eureka tracker notifications.')
    @check(PermissionValidator.is_admin)
    async def add_eureka_role(self, interaction: Interaction, instance: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_eureka_instance(interaction, instance): return
        pings_data = bot.instance.data.guilds.get(interaction.guild_id).pings
        pings_data.add_ping(GuildPingType.EUREKA_TRACKER_NOTIFICATION, instance, role.id)
        feedback = f'added a ping for role **{EurekaTrackerZone(int(instance)).name}**.'
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** {feedback}')
        await default_response(interaction, 'You ' + feedback)

    @command(name='remove_eureka_role', description='Remove a ping for eureka tracker notifications.')
    @check(PermissionValidator.is_admin)
    async def remove_eureka_role(self, interaction: Interaction, instance: str, role: Role):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_valid_eureka_instance(interaction, instance): return
        pings_data = bot.instance.data.guilds.get(interaction.guild_id).pings
        pings_data.remove_ping(GuildPingType.EUREKA_TRACKER_NOTIFICATION, instance, role.id)
        feedback = f'removed a ping for role **{EurekaTrackerZone(int(instance)).name}**.'
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** {feedback}')
        await default_response(interaction, 'You ' + feedback)

    @add_role.autocomplete('event_type')
    @remove_role.autocomplete('event_type')
    async def autocomplete_event_type_with_categories(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_type_with_categories(current)

    @add_role.autocomplete('ping_type')
    @remove_role.autocomplete('ping_type')
    async def autocomplete_ping_type(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.ping_type(current)

    @add_eureka_role.autocomplete('instance')
    @remove_eureka_role.autocomplete('instance')
    async def autocomplete_eureka_instance(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.eureka_instance(current)

    #region error-handling
    @add_role.error
    @remove_role.error
    @add_eureka_role.error
    @remove_eureka_role.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command  or an error has occured.', ephemeral=True)
    #endregion
