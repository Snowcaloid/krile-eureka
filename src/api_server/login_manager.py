from dataclasses import asdict
from flask_jwt_extended import JWTManager, create_access_token
from data.db.sql import SQL, Record
from centralized_data import Bindable
from api_server.permission_manager import PermissionManager

from typing import Any, List, override

class User:
    def __init__(self, token: str, id: int, name: str) -> None:
        self.token = token
        self.id = id
        self.name = name

class LoginManager(Bindable):
    from api_server import ApiServer
    @ApiServer.bind
    def api_server(self) -> ApiServer: ...

    @override
    def constructor(self) -> None:
        super().constructor()
        self._jwt_manager = JWTManager(self.api_server)
        self._user_cache: List[User] = []
        self.load()

    def load(self) -> None:
        self._user_cache.clear()
        for record in SQL('api_users').select(fields=['token', 'name', 'id']):
            self._user_cache.append(User(record['token'], record['id'], record['name']))

    def get_user(self, id: int) -> User:
        return next((user for user in self._user_cache if user.id == id), None)

    def refresh_user_token(self, token: str) -> str:
        user = next((user for user in self._user_cache if user.token == token), None)
        if user is None: return None
        permissions = PermissionManager(user.id).calculate()
        token = create_access_token(
            identity=user,
            additional_claims={ "permissions": [asdict(permission) for permission in permissions] } )
        SQL('api_users').update(Record(token=token), f'id={user.id}')
        self.load()
        return token

    def set_user(self, id: int, name: str) -> str:
        user = self.get_user(id)
        if user is not None:
            return self.refresh_user_token(user.token)

        user = User(None, id, name)
        permissions = PermissionManager(id).calculate()
        token = create_access_token(
            identity=user,
            additional_claims={ "permissions": [asdict(permission) for permission in permissions] } )
        SQL('api_users').insert(Record(token=token, id=id, name=name))
        self.load()
        return token

lm = LoginManager()

@lm._jwt_manager.user_identity_loader
def user_identity_loader(user: User) -> str:
    return str(user.id)

@lm._jwt_manager.user_lookup_loader
def user_lookup_loader(jwt_header: Any, jwt_data: Any) -> User:
    identity = jwt_data.get('sub')
    if identity is None: return None
    return lm.get_user(int(identity))