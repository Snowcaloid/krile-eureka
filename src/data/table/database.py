from enum import Enum
import psycopg2
import os
from datetime import datetime

def pg_timestamp(timestamp: datetime):
    return timestamp.strftime("\'%Y-%m-%d %H:%M\'")


class DatabaseOperation(Enum):
    ADDED = 0
    EDITED = 1


class Database:
    _connection_counter: int = 0
    _connection: None
    _cursor: None

    def connect(self):
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

    def disconnect(self):
        if not self._connection_counter:
            raise Exception('disconnect without prior connect')

        self._connection_counter -= 1
        if not self._connection_counter:
            self._connection.commit()
            self._connection.close()

    def query(self, query: str):
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
