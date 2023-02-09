from typing import List

class ColumnType:
    INTEGER = 'INTEGER'
    DATE = 'DATE'
    BOOLEAN = 'BOOLEAN'
    VARCHAR = 'VARCHAR'
    
class ColumnFlag:
    NONE = ''
    PRIMARY_KEY = 'PRIMARY KEY'
    UNIQUE = 'UNIQUE'

class ColumnDefinition:
    name: str = ''
    type: str = ''
    length: int = 0
    flags: List[ColumnFlag] = [ColumnFlag.NONE]
    def __init__(self, name: str, type: ColumnType, length: int = 0, flags: List[ColumnFlag] = []):
        self.name = name
        self.type = type
        self.length = length
        self.flags = flags
        
class TableDefinition:
    _name: str = ''
    _columns: List[ColumnDefinition] = []
    
    def __init__(self, name: str):
        self._name = name
        self.init_definitions()

    def init_definitions(self):
        pass
    
    def define_field(self, name: str, type: ColumnType, length: int = 0, flags: List[ColumnFlag] = [ColumnFlag.NONE]):
        self._columns.append(ColumnDefinition(name, type, length, flags)) 
        
    def to_sql_create(self) -> str:
        return f'CREATE TABLE IF NOT EXISTS {self._name}()'
    
    def to_sql_alter(self) -> str:
        columns = ''
        for column in self._columns:
            len = f'({str(column.length)})' if column.length > 0 else '' 
            flags = ''
            for flag in column.flags:
                if flag != ColumnFlag.NONE:
                    if flags:
                        flags = ' '.join([flags, flag])
                    else:
                        flags = flag
                    
            if columns:
                columns = ','.join([columns, f'ADD COLUMN IF NOT EXISTS {column.name} {column.type}{len} {flags}'])
            else:
                columns = f'ADD COLUMN IF NOT EXISTS {column.name} {column.type}{len} {flags}'
        
        new_line = "\n"    
        return f'ALTER TABLE {self._name}{new_line}{columns}'
        
class TableDefinitions:
    DEFINITIONS: List[TableDefinition] = []
    
    @classmethod
    def register(cls, table: TableDefinition):
        cls.DEFINITIONS.append(table)
    