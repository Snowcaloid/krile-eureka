from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Self, Tuple, TypeVar, Union, overload, override

from data.db.database import Database, PgColumnValue, pg_timestamp
from utils.basic_types import Unassigned
from utils.functions import is_null_or_unassigned

SQL_ALL_FIELDS = ['*']

class Record(Dict[str, PgColumnValue]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Any:
        if super().__getitem__(key) is None: return Unassigned
        return super().__getitem__(key)

    def _enum_db_value(self, enum: Enum):
        return None if is_null_or_unassigned(enum) else enum.value

    def __setitem__(self, key: str, value: PgColumnValue) -> None:
        if isinstance(value, Enum): super().__setitem__(key, self._enum_db_value(value))
        elif value is Unassigned: super().__setitem__(key, None)
        else: super().__setitem__(key, value)

class _BasicConnection(ABC):
    def __init__(self):
        self._database = Database()

    def __enter__(self) -> Self:
        self._database.connect()
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...

    def sql(self, table_name: str) -> _SQL:
        """Create a SQL object for the given table name."""
        return _SQL(table_name, self)

    def custom_sql(self, statement: str) -> List[PgColumnValue]:
        """Execute a custom SQL statement."""
        return self._database.query(statement)

class Transaction(_BasicConnection):
    @override
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._database.disconnect(exc_type is None)
        if exc_type is not None: raise

class ReadOnlyConnection(_BasicConnection):
    @override
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._database.disconnect(False)
        if exc_type is not None: raise


class Records(List[Record]): ...


class _SQL:
    def __init__(self, table_name: str, connection: _BasicConnection):
        self.table_name = table_name
        self._connection = connection

    def _get_all_fields(self) -> List[str]:
        with ReadOnlyConnection() as connection:
            records = self.__class__('information_schema.columns', connection).select(
                fields=['column_name'],
                where=f'table_name = \'{self.table_name}\'',
                all=True)
            if not isinstance(records, Records):
                raise Exception(f'Table {self.table_name} does not exist.')

            return [str(record['column_name']) for record in records]

    def _convert_to_sql(self, value: PgColumnValue) -> str:
        if isinstance(value, (int, bool)):
            return str(value)
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, datetime):
            return pg_timestamp(value)
        return 'null'

    def select(self, *,
               fields: List[str] = SQL_ALL_FIELDS,
               where: str = '',
               filter: Optional[Record] = None,
               all: bool = True,
               sort_fields: List[str | Tuple[str, bool]] = [],
               group_by: List[str] = []) -> Records:
        if fields == SQL_ALL_FIELDS: fields = self._get_all_fields()
        if all is None: all = where == ''
        sql_statement = f'select {", ".join(fields)} from {self.table_name}'
        if filter is not None:
            where = ' and '.join([
                f'({field} is null or not {field})' # False filtering for booleans...
                if isinstance(filter[field], bool) and filter[field] == False
                else f'{field} = {self._convert_to_sql(filter[field])}'
                for field in filter.keys()
            ])
        if where:
            sql_statement += f' where {where}'
        if sort_fields:
            sort_fields = [(sort_field, True) if not isinstance(sort_field, tuple) else sort_field for sort_field in sort_fields]
            sql_statement += f' order by {", ".join([f"{sort[0]} {'asc' if sort[1] else 'desc'}" for sort in sort_fields])}'
        if group_by: sql_statement += ' group by ' + ', '.join(group_by)
        if not all: sql_statement += ' limit 1'
        records = Records()
        for sql_record in self._connection.custom_sql(sql_statement):
            if not isinstance(sql_record, list): continue
            record = Record()
            for i, field in enumerate(fields):
                record[field] = sql_record[i]
            records.append(record)
            if not all: break
        return records

    def insert(self, record: Record, returning_field: str = '') -> PgColumnValue:
        fields = ', '.join(record.keys())
        values = ', '.join([self._convert_to_sql(value) for value in record.values()])
        returning = f' returning {returning_field}' if returning_field else ''
        return self._connection.custom_sql(f'insert into {self.table_name} ({fields}) values ({values}){returning}')

    @overload
    def update(self, record: Record, condition: Record) -> None: ...
    """Update records in the table based on a Record."""

    @overload
    def update(self, record: Record, condition: str) -> None: ...
    """Update records in the table based on a Record and a where clause."""

    def update(self, record: Record, condition: Union[Record, str]) -> None:
        set_fields = ', '.join([f'{field} = {self._convert_to_sql(value)}' for field, value in record.items()])
        if isinstance(condition, str):
            where = condition
        elif isinstance(condition, Record):
            where = ' and '.join([f'{field} = {self._convert_to_sql(value)}' for field, value in condition.items()])
        else:
            raise TypeError(f'Unsupported type for condition: {type(condition)}')
        self._connection.custom_sql(f'update {self.table_name} set {set_fields} where {where}')

    @overload
    def delete(self, condition: str) -> None: ...
    """Delete records from the table based on a where clause."""

    @overload
    def delete(self, condition: Record) -> None: ...
    """Delete records from the table based on a Record."""

    def delete(self, condition: Union[str, Record]) -> None:
        if isinstance(condition, str):
            self._connection.custom_sql(f'delete from {self.table_name} where {condition}')
        elif isinstance(condition, Record):
            where = ' and '.join([f'{field} = {self._convert_to_sql(condition[field])}' for field in condition.keys()])
            self._connection.custom_sql(f'delete from {self.table_name} where {where}')
        raise TypeError(f'Unsupported type for delete: {type(condition)}')

    def drop(self) -> None:
        self._connection.custom_sql(f'drop table if exists {self.table_name}')