from typing import List

class ColumnType:
    INTEGER = 'INTEGER'
    TIMESTAMP = 'TIMESTAMP'
    BOOLEAN = 'BOOLEAN'
    VARCHAR = 'VARCHAR'
    BIGINT = 'BIGINT'
    SERIAL = 'SERIAL'
    TEXT = 'TEXT'
    
class ColumnFlag:
    NONE = ''
    PRIMARY_KEY = 'PRIMARY KEY'
    UNIQUE = 'UNIQUE'

class ColumnDefinition:
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
    _name: str
    _columns: List[ColumnDefinition]
    
    def __init__(self, name: str):
        self._name = name
        self._columns = []
        self.init_definitions()

    def init_definitions(self):
        pass
    
    def define_field(self, name: str, type: ColumnType, length: int = 0, 
                     flags: List[ColumnFlag] = [ColumnFlag.NONE], references: str = ''):
        self._columns.append(ColumnDefinition(name, type, length, flags, references)) 
        
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
                columns = ",\n".join([columns, f'add column if not exists {column.name} {column.type}{len} {flags}'])
            else:
                columns = f'add column if not exists {column.name} {column.type}{len} {flags}'
            
            if column.references:
                if columns:
                    columns = ",\n".join([columns, f'drop constraint if exists c_{column.name}'])
                else:
                    columns = f'drop constraint if exists c_{column.name}'
                    
                columns = ",\n".join([columns, f'add constraint c_{column.name} foreign key({column.name}) references {column.references}'])
        
        new_line = "\n"  
        return f'alter table {self._name}{new_line}{columns}'
        
class TableDefinitions:
    DEFINITIONS: List[TableDefinition] = []
    
    @classmethod
    def register(cls, table: TableDefinition):
        cls.DEFINITIONS.append(table)
    