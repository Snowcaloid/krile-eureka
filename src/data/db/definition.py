from typing import List, Type, override

from centralized_data import YamlAsset, YamlAssetLoader
from centralized_data import YamlAsset, YamlAssetLoader
from discord import Client

from data.db.sql import SQL, Batch, Record
from utils.functions import filter_choices_by_current, is_null_or_unassigned
from discord.app_commands import Choice

class TableDefinition(YamlAsset):
    @property
    def name(self) -> str:
        return self.source.get("name", "")

    @property
    def columns(self) -> List[dict]:
        return self.source.get("columns", [])

    def to_sql_create(self) -> str:
        """Get Create Table SQL statement."""
        return f'CREATE TABLE IF NOT EXISTS {self.name}()'

    def to_sql_alter(self) -> str:
        """Get Alter Table SQL statement."""
        columns = ''
        for column_object in self.columns:
            column: dict = column_object
            unique = 'unique' if column.get('unique', False) else ''

            if columns:
                columns = ", ".join([columns, f'add column if not exists {column["name"]} {column["type"]} {unique}'])
            else:
                columns = f'add column if not exists {column["name"]} {column["type"]} {unique}'

            if column.get("primary_key", False):
                txt = f'drop constraint if exists {self.name}_pkey, add primary key ({column["name"]})'
                if columns:
                    columns = ", ".join([columns, txt])
                else:
                    columns = txt

        return f'alter table {self.name} {columns}'

class TableDefinitions(YamlAssetLoader[TableDefinition]):
    @override
    def asset_folder_name(self) -> str: return 'db_tables'

    @override
    def asset_class(self) -> Type[TableDefinition]: return TableDefinition

    def _migrate_pings_to_roles(self) -> None:
        if next((table for table in self.loaded_assets if table.name == 'pings'), None) is None:
            return

        for record in SQL('pings').select(all=True):
            if is_null_or_unassigned(record['ping_type']):
                record['ping_type'] += 3 #type: ignore

            SQL('roles').insert(Record(
                guild_id=record['guild_id'],
                role_id=record['tag'],
                event_type=record['schedule_type'],
                function=record['ping_type']
            ))
            SQL('pings').delete(f'id={record["id"]}')
        SQL('pings').drop()

    def _migrate_events_to_event_users(self) -> None:
        events_table = next((table for table in self.loaded_assets if table.name == 'events'))
        assert events_table is not None, "Events table not loaded."
        if next((True for column in events_table.columns if column.get('name') == 'pl1'), None) is not None:
            return

        for record in SQL('events').select(all=True):
            users = [
                record['pl1'], record['pl2'], record['pl3'],
                record['pl4'], record['pl5'], record['pl6'],
                record['pls']
            ]
            for i, user_id in enumerate(users):
                if user_id is None: continue
                user_name = '<migrated user, name not available>'
                SQL('event_users').insert(Record(
                    event_id=record['id'],
                    user_id=user_id,
                    user_name=user_name,
                    party=i+1,
                    is_party_leader=True
                ))
            SQL('events').update(Record(
                pl1=None, pl2=None, pl3=None,
                pl4=None, pl5=None, pl6=None,
                pls=None
            ), where=f'id={record["id"]}')

        with Batch() as batch:
            batch._database.query('alter table events drop column if exists pl1')
            batch._database.query('alter table events drop column if exists pl2')
            batch._database.query('alter table events drop column if exists pl3')
            batch._database.query('alter table events drop column if exists pl4')
            batch._database.query('alter table events drop column if exists pl5')
            batch._database.query('alter table events drop column if exists pl6')
            batch._database.query('alter table events drop column if exists pls')

    def execute_migrations(self) -> None:
        self._migrate_pings_to_roles()
        self._migrate_events_to_event_users()

    @classmethod
    def autocomplete(cls, current: str) -> List[Choice]:
        return filter_choices_by_current([Choice(name=definition.name, value=definition.name) for definition in cls().loaded_assets], current)

    @override
    def constructor(self, client: Client) -> None:
        super().constructor()
        self.client = client

        with Batch() as batch:
            for table in self.loaded_assets:
                batch._database.query(table.to_sql_create())
                batch._database.query(table.to_sql_alter())

            self.execute_migrations()