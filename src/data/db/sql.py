from datetime import datetime
from enum import Enum
from functools import wraps
from sys import exc_info
from typing import Any, Callable, Dict, List, Tuple, TypeVar

from data.db.database import Database, PgColumnValue, pg_timestamp
from utils.basic_types import STRUCT_NULL, Unassigned

SQL_ALL_FIELDS = ['*']

class Record(Dict[str, PgColumnValue]):
    DATABASE: Database = Database()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.DATABASE.connect()

    def __del__(self):
        self.DATABASE.disconnect()

    def __getitem__(self, key: str) -> PgColumnValue:
        if super().__getitem__(key) is None: return Unassigned
        return super().__getitem__(key)

    def _enum_db_value(self, enum: Enum):
        return enum.value if enum is not None and enum is not STRUCT_NULL else None

    def __setitem__(self, key: str, value: PgColumnValue) -> None:
        if isinstance(value, Enum): super().__setitem__(key, self._enum_db_value(value))
        elif value is Unassigned: super().__setitem__(key, None)
        else: super().__setitem__(key, value)

class Transaction(Record):
    def __exit__(self, exc_type, exc_value, traceback):
        self.DATABASE.disconnect(exc_type is None)

class Batch(Record):
    def __exit__(self, exc_type, exc_value, traceback):
        self.DATABASE.disconnect()

T = TypeVar('T', bound=Callable[..., Any])

class Records(List[Record]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Record.DATABASE.connect()

    def __del__(self):
        Record.DATABASE.disconnect()


class SQL:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _get_all_fields(self) -> List[str]:
        records = Record().DATABASE.query(f"select column_name FROM information_schema.columns WHERE table_name = '{self.table_name}'")
        if records is None or len(records) == 0:
            raise Exception(f'Table {self.table_name} does not exist.')

        return [record[0] for record in records]

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
               all: bool = None,
               sort_fields: List[str | Tuple[str, bool]] = [],
               group_by: List[str] = []) -> Record | Records:
        if fields == SQL_ALL_FIELDS: fields = self._get_all_fields()
        if all is None: all = where == ''
        sql_statement = f'select {", ".join(fields)} from {self.table_name}'
        if where: sql_statement += f' where {where}'
        if sort_fields:
            sort_fields = [(sort_field, True) if not isinstance(sort_field, tuple) else sort_field for sort_field in sort_fields]
            sql_statement += f' order by {", ".join([f"{sort[0]} {'asc' if sort[1] else 'desc'}" for sort in sort_fields])}'
        if group_by: sql_statement += ' group by ' + ', '.join(group_by)
        if not all: sql_statement += ' limit 1'
        if all: records = Records()
        sql_records = Record().DATABASE.query(sql_statement)
        for sql_record in sql_records:
            record = Record()
            for i, field in enumerate(fields):
                record[field] = sql_record[i]
            if all:
                records.append(record)
            else:
                return record
        return records if all else None

    def insert(self, record: Record, returning_field: str = None) -> PgColumnValue:
        fields = ', '.join(record.keys())
        values = ', '.join([self._convert_to_sql(value) for value in record.values()])
        returning = f' returning {returning_field}' if returning_field else ''
        return record.DATABASE.query(f'insert into {self.table_name} ({fields}) values ({values}){returning}')

    def update(self, record: Record, where: str) -> None:
        set_fields = ', '.join([f'{field} = {self._convert_to_sql(value)}' for field, value in record.items()])
        record.DATABASE.query(f'update {self.table_name} set {set_fields} where {where}')

    def delete(self, where: str) -> None:
        Record().DATABASE.query(f'delete from {self.table_name} where {where}')

    def drop(self) -> None:
        Record().DATABASE.query(f'drop table if exists {self.table_name}')