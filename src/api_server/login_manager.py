from uuid import uuid4
from basic_types import UserUUID
from data.db.sql import SQL, Record
from centralized_data import Bindable

from typing import Dict, override

class User:
    def __init__(self, uuid: UserUUID, id: int, name: str) -> None:
        self.uuid = uuid
        self.id = id
        self.name = name

class LoginManager(Bindable):
    @override
    def constructor(self) -> None:
        super().constructor()
        self._user_cache: Dict[UserUUID, User] = {}
        self.load()

    def load(self) -> None:
        self._user_cache.clear()
        for record in SQL('api_users').select(fields=['uuid', 'name', 'id']):
            self._user_cache[record['uuid']] = User(record['uuid'], record['id'], record['name'])

    def get_user(self, uuid: str) -> User:
        return self._user_cache.get(uuid)

    def set_user(self, id: int, name: str) -> str:
        user = next((user for user in self._user_cache.values() if user.id == id), None)
        if user is not None:
            return user.uuid

        uuid = UserUUID(uuid4())
        SQL('api_users').insert(Record(uuid=uuid, id=id, name=name))
        self.load()
        return uuid