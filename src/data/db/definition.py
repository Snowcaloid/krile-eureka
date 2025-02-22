from typing import Type, override

from centralized_data import YamlAsset, YamlAssetLoader

class TableDefinition(YamlAsset):

    def name(self) -> str:
        return self.source["name"]

    def to_sql_create(self) -> str:
        """Get Create Table SQL statement."""
        return f'CREATE TABLE IF NOT EXISTS {self.name()}()'

    def to_sql_alter(self) -> str:
        """Get Alter Table SQL statement."""
        columns = ''
        for column_object in self.source["columns"]:
            column: object = column_object
            unique = 'unique' if column.get('unique', False) else ''

            if columns:
                columns = ", ".join([columns, f'add column if not exists {column["name"]} {column["type"]} {unique}'])
            else:
                columns = f'add column if not exists {column["name"]} {column["type"]} {unique}'

            if column.get("primary_key", False):
                txt = f'drop constraint if exists {self.name()}_pkey, add primary key ({column["name"]})'
                if columns:
                    columns = ", ".join([columns, txt])
                else:
                    columns = txt

        return f'alter table {self.name()} {columns}'

class TableDefinitions(YamlAssetLoader[TableDefinition]):
    @override
    def asset_folder_name(self) -> str: return 'db_tables'

    @override
    def asset_class(self) -> Type[TableDefinition]: return TableDefinition