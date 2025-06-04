from enum import Enum
from typing import Any, List, Union
import psycopg2
import os
from datetime import datetime

from utils.basic_types import _Unassigned


def pg_timestamp(timestamp: datetime):
    return timestamp.strftime("\'%Y-%m-%d %H:%M\'")


PgColumnValue = Union[Any, str, int, bool, datetime, _Unassigned]


class DatabaseOperation(Enum):
    """Used to inform the type of database operation performed."""
    NONE = 0
    """No operation was performed (the record did not need updating)"""
    ADDED = 1
    """A new record was created."""
    EDITED = 2
    """An existing record was updated."""


class Database:
    """Runtime database access object

    Properties
    ----------
    _connection_counter: :class:`int`
        Depth of connection requests. When the counter reaches 0,
        database will commit changes and close the connection.
    _connection: :class:`pgConnection`
        Currently opened connection.
    _cursor: :class: `pgCursor`
        Currently used cursor for the connection
    """
    _connection_counter: int = 0
    _connection: None
    _cursor: None

    def connected(self):
        return self._connection_counter > 0

    def connect(self):
        """Connect to Postgres. If already active, _connection_counter is incremented."""
        if not self._connection_counter:
            self._connection = psycopg2.connect(
                database=os.getenv('DB_NAME'),
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                port=os.getenv('DB_PORT')
            )
            self._cursor = self._connection.cursor()

        self._connection_counter += 1

    def disconnect(self, commit: bool = True):
        """Disconnect from Postgres and save the changes. If multiple
        `connect()`'s were called, the _connection_counter is decremented."""
        if not self._connection_counter:
            raise Exception('disconnect without prior connect')

        self._connection_counter -= 1
        if not self._connection_counter:
            if commit:
                self._connection.commit()
            else:
                self._connection.rollback()
            self._connection.close()

    def query(self, query: str) -> List[PgColumnValue]:
        """Execute a query on the current cursor.

        Args:
            query (str): SQL string to be executed.

        Returns:
            Union[str, None]:
                SELECT statement returns an array of row arrays.

                INSERT INTO RETURNING returns the value which is requested.

                Other queries return an empty array.
        """
        self.connect()
        try:
            self._cursor.execute(query)
            if 'select' in query:
                return self._cursor.fetchall()
            elif 'returning' in query:
                return self._cursor.fetchone()[0]
            else:
                return []
        finally:
            self.disconnect()
