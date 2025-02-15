from typing import List

class ColumnType:
    INTEGER = 'INTEGER'
    TIMESTAMP = 'TIMESTAMP'
    BOOLEAN = 'BOOLEAN'
    VARCHAR = 'VARCHAR'
    BIGINT = 'BIGINT'
    SERIAL = 'SERIAL'
    TEXT = 'TEXT'
    JSON = 'JSON'

class ColumnFlag:
    NONE = ''
    PRIMARY_KEY = 'PRIMARY KEY'
    UNIQUE = 'UNIQUE'

class ColumnDefinition:
    """Helper class containing a column definition for a table."""
    name: str
    type: str
    length: int
    flags: List[ColumnFlag]
    references: str
    def __init__(self, name: str, type: ColumnType, length: int = 0, flags: List[ColumnFlag] = [], references: str = ''):
        self.name = name
        self.type = type
        self.length = length
        self.flags = flags
        self.references = references

class TableDefinition:
    """Table definition class. Any table can inherit this class and define
    it's columns in the method `init_definitons`.

    Properties
    ----------
    _name: :class:`str`
        Table name.
    _columns: :class:`List[ColumnDefinition]`
        List of column definitions.
    """
    _name: str
    _columns: List[ColumnDefinition]

    def __init__(self, name: str):
        self._name = name
        self._columns = []
        self.init_definitions()

    def init_definitions(self):
        """Override this function in classes that inherit this to define columns."""
        pass

    def define_column(self, name: str, type: ColumnType, length: int = 0,
                     flags: List[ColumnFlag] = [ColumnFlag.NONE], references: str = ''):
        """Add a column

        Args:
            name (str): Column name
            type (ColumnType): Column type
            length (int, optional): Column length (only viable for VARCHAR). Defaults to 0.
            flags (List[ColumnFlag], optional): Column flags (e.g. Primary key, Unique). Defaults to [ColumnFlag.NONE].
            references (str, optional): Refence to a primary key of another table. Experimental. Defaults to ''.
        """
        self._columns.append(ColumnDefinition(name, type, length, flags, references))

    def to_sql_create(self) -> str:
        """Get Create Table SQL statement."""
        return f'CREATE TABLE IF NOT EXISTS {self._name}()'

    def to_sql_alter(self) -> str:
        """Get Alter Table SQL statement."""
        columns = ''
        for column in self._columns:
            len = f'({str(column.length)})' if column.length > 0 else ''
            flags = ''
            for flag in column.flags:
                if not flag in [ColumnFlag.NONE, ColumnFlag.PRIMARY_KEY]:
                    if flags:
                        flags = ' '.join([flags, flag])
                    else:
                        flags = flag

            if columns:
                columns = ", ".join([columns, f'add column if not exists {column.name} {column.type}{len} {flags}'])
            else:
                columns = f'add column if not exists {column.name} {column.type}{len} {flags}'

            if ColumnFlag.PRIMARY_KEY in column.flags:
                txt = f'drop constraint if exists {self._name}_pkey, add primary key ({column.name})'
                if columns:
                    columns = ", ".join([columns, txt])
                else:
                    columns = txt

            if column.references:
                if columns:
                    columns = ", ".join([columns, f'drop constraint if exists c_{column.name}'])
                else:
                    columns = f'drop constraint if exists c_{column.name}'

                columns = ", ".join([columns, f'add constraint c_{column.name} foreign key({column.name}) references {column.references}'])

        return f'alter table {self._name} {columns}'

class TableDefinitions:
    """Definition list of all tables. Use TableDefinitions.register() to
    create persistent tables in the database."""
    DEFINITIONS: List[TableDefinition] = []

    @classmethod
    def clear(cls):
        cls.DEFINITIONS.clear()

    @classmethod
    def register(cls, table: TableDefinition):
        cls.DEFINITIONS.append(table)
