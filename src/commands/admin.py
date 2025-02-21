from typing import Optional

import pandas
import bot
from discord.ext.commands import GroupCog
from discord.app_commands import check, command
from discord import Interaction
from data.db.definition import TableDefinitions
from data.db.sql import Record
from data.generators.autocomplete_generator import AutoCompleteGenerator
from data.validation.input_validator import InputValidator
from utils import default_defer, default_response
from data.validation.permission_validator import PermissionValidator
from logger import guild_log_message


class AdminCommands(GroupCog, group_name='admin', group_description='Bot administrator commands.'):
    @command(name = "query", description = "Does a select query over a table.")
    @check(PermissionValidator.is_admin)
    async def query(self, interaction: Interaction, table: str, fields: Optional[str] = '*', filter: Optional[str] = '', order: Optional[str] = ''):
        await default_defer(interaction)
        if not await InputValidator.RAISING.check_for_sql_identifiers(interaction, filter): return
        if not await InputValidator.RAISING.check_for_sql_identifiers(interaction, order): return
        if not await InputValidator.RAISING.check_for_sql_identifiers(interaction, fields): return
        where = f' where {filter}' if filter else ''
        order_by = f' order by {order}' if order else ''
        if fields == '*':
            column_names = [column["name"] for column in next(
                (definition for definition in TableDefinitions().loaded_assets if definition.name() == table), None).source["columns"]]
        else:
            column_names = [name.strip() for name in fields.split(',')]
        result = Record().DATABASE.query(f'select {fields} from {table}{where}{order_by} limit 25')
        pandas.set_option('display.expand_frame_repr', False)
        pandas.set_option('display.width', 240)
        response = pandas.DataFrame(result, columns=column_names)
        response = f'```\n{response}\n```'
        await default_response(interaction, response)


    @command(name = "reload", description = "Loads all bot data from the database again.")
    @check(PermissionValidator.is_owner)
    async def reload(self, interaction: Interaction):
        await default_defer(interaction)
        await bot.instance.data.reset()
        await default_response(interaction, 'Successfully reloaded.')


    @query.autocomplete('table')
    async def autocomplete_table(self, interaction: Interaction, current: str):
        return AutoCompleteGenerator.table(current)


    #region error-handling
    @query.error
    @reload.error
    async def handle_error(self, interaction: Interaction, error):
        print(error)
        await guild_log_message(interaction.guild_id, f'**{interaction.user.display_name}**: {str(error)}')
        if interaction.response.is_done():
            if interaction.followup:
                await interaction.followup.send('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
        else:
            await interaction.response.send_message('You have insufficient rights to use this command or an error has occured.', ephemeral=True)
    #endregion