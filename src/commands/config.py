import bot
import data.cache.message_cache as cache
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Embed, Interaction
from discord.channel import TextChannel
from data.events.event import Event, EventCategory
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.validation.input_validator import InputValidator
from utils import default_defer, default_response, set_default_footer
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message


class ConfigCommands(GroupCog, group_name='config', group_description='Config commands.'):
    @command(name = "create_schedule_post", description = "Initialize the server\'s schedule by creating a static post that will be used as an event list.")
    @check(PermissionValidator.is_admin)
    async def create_schedule_post(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        schedule = bot.instance.data.guilds.get(interaction.guild_id).schedule
        if schedule.schedule_post.id:
            old_channel = bot.instance.get_channel(schedule.schedule_post.channel)
            old_message = await cache.messages.get(schedule.schedule_post.id, old_channel)
            if old_message:
                await old_message.delete()
        message = await channel.send(embed=Embed(description='...'))
        await set_default_footer(message)
        bot.instance.data.guilds.get(interaction.guild_id).schedule.schedule_post.set(message.id, channel.id)
        await bot.instance.data.ui.schedule.rebuild(interaction.guild_id)
        await default_response(interaction, f'Schedule has been created in #{channel.name}')
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}** has created a schedule post in #{channel.name}.')

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

    @command(name = "create_missed_run_list", description = "Create a missed run list.")
    @check(PermissionValidator.is_admin)
    async def create_missed_run_list(self, interaction: Interaction, channel: TextChannel):
        await default_defer(interaction)
        message = await channel.send(embed=Embed(description='...'))
        data = bot.instance.data
        data.guilds.get(interaction.guild_id).channels.set(channel.id, GuildChannelFunction.MISSED_POST_CHANNEL)
        data.guilds.get(interaction.guild_id).missed_runs.assign_message(message.id)
        await data.ui.missed_runs_list.rebuild(interaction.guild_id)
        await default_response(interaction, f'Missed run post has been created in #{channel.name}.')

    @passcode_channel.autocomplete('event_type')
    @party_leader_channel.autocomplete('event_type')
    @support_passcode_channel.autocomplete('event_type')
    async def autocomplete_schedule_type_with_all(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.event_type_with_categories(current)

    #region error-handling
    @create_schedule_post.error
    @passcode_channel.error
    @support_passcode_channel.error
    @party_leader_channel.error
    @create_missed_run_list.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion