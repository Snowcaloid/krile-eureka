from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Self, Tuple, TypeVar, Union, overload

from data.db.database import Database, PgColumnValue, pg_timestamp
from utils.basic_types import Unassigned
from utils.functions import is_null_or_unassigned

SQL_ALL_FIELDS = ['*']

class Record(Dict[str, PgColumnValue]):
    @Database.bind
    def _database(self) -> Database: ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database.connect()

    def __enter__(self) -> Self:
        return self

    def __del__(self):
        self._database.disconnect()

    def __getitem__(self, key: str) -> PgColumnValue:
        if super().__getitem__(key) is None: return Unassigned
        return super().__getitem__(key)

    def _enum_db_value(self, enum: Enum):
        return None if is_null_or_unassigned(enum) else enum.value

    def __setitem__(self, key: str, value: PgColumnValue) -> None:
        if isinstance(value, Enum): super().__setitem__(key, self._enum_db_value(value))
        elif value is Unassigned: super().__setitem__(key, None)
        else: super().__setitem__(key, value)

class Transaction(Record):
    def __exit__(self, exc_type, exc_value, traceback):
        self._database.disconnect(exc_type is None)

class Batch(Record):
    def __exit__(self, exc_type, exc_value, traceback):
        self._database.disconnect()


T = TypeVar('T', bound=Callable[..., Any])


class Records(List[Record]):
    @Database.bind
    def _database(self) -> Database: ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database.connect()

    def __del__(self):
        self._database.disconnect()


class SQL:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _get_all_fields(self) -> List[str]:
        records = self.__class__('information_schema.columns').select(
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
               all: bool = True,
               sort_fields: List[str | Tuple[str, bool]] = [],
               group_by: List[str] = []) -> Records:
        if fields == SQL_ALL_FIELDS: fields = self._get_all_fields()
        if all is None: all = where == ''
        sql_statement = f'select {", ".join(fields)} from {self.table_name}'
        if where: sql_statement += f' where {where}'
        if sort_fields:
            sort_fields = [(sort_field, True) if not isinstance(sort_field, tuple) else sort_field for sort_field in sort_fields]
            sql_statement += f' order by {", ".join([f"{sort[0]} {'asc' if sort[1] else 'desc'}" for sort in sort_fields])}'
        if group_by: sql_statement += ' group by ' + ', '.join(group_by)
        if not all: sql_statement += ' limit 1'
        records = Records()
        with Batch() as batch:
            for sql_record in batch._database.query(sql_statement):
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
        return record._database.query(f'insert into {self.table_name} ({fields}) values ({values}){returning}')

    def update(self, record: Record, where: str) -> None:
        set_fields = ', '.join([f'{field} = {self._convert_to_sql(value)}' for field, value in record.items()])
        record._database.query(f'update {self.table_name} set {set_fields} where {where}')

    @overload
    def delete(self, condition: str) -> None: ...
    """Delete records from the table based on a where clause."""

    @overload
    def delete(self, condition: Record) -> None: ...
    """Delete records from the table based on a Record."""

    def delete(self, condition: Union[str, Record]) -> None:
        if isinstance(condition, str):
            Record()._database.query(f'delete from {self.table_name} where {condition}')
        elif isinstance(condition, Record):
            where = ' and '.join([f'{field} = {self._convert_to_sql(condition[field])}' for field in condition.keys()])
            Record()._database.query(f'delete from {self.table_name} where {where}')
        raise TypeError(f'Unsupported type for delete: {type(condition)}')

    def drop(self) -> None:
        Record()._database.query(f'drop table if exists {self.table_name}')