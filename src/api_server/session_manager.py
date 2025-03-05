from dataclasses import asdict, dataclass
from datetime import timedelta
from flask import request
from flask_jwt_extended import JWTManager, create_access_token, current_user, get_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import UserClaimsVerificationError
from api_server import ApiNamespace
from data.db.sql import SQL, Record
from centralized_data import Bindable
from api_server.permission_manager import PermissionManager

from typing import Any, Dict, List, override

@dataclass
class User:
    id: int
    name: str
    user_token: str = None
    session_token: str = None

class SessionManager(Bindable):
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
        for record in SQL('api_users').select(fields=['id', 'name', 'user_token', 'session_token']):
            self._user_cache.append(User(record['id'], record['name'], record['user_token'], record['session_token']))

    def get_user_by_id(self, id: int) -> User:
        return next((user for user in self._user_cache if user.id == id), None)

    def get_user_by_token(self, token: str) -> User:
        return next((user for user in self._user_cache if user.user_token == token), None)

    def get_user_by_session_token(self, token: str) -> User:
        return next((user for user in self._user_cache if user.session_token == token), None)

    def add_user(self, id: int, name: str) -> User:
        SQL('api_users').insert(Record(id=id, name=name))
        self.load()
        return self.get_user_by_id(id)

    def login(self, user: User) -> str:
        user.user_token = create_access_token(identity=user, expires_delta=False) # this isnt a refresh token because i'm lazy
        SQL('api_users').update(Record(user_token=user.user_token), f'id={user.id}')
        self.load()
        return user.user_token

    def open_session(self, user: User) -> str:
        user.session_token = create_access_token(
            identity=user,
            additional_claims={
                "permissions": [asdict(permission) for permission in PermissionManager(user.id).calculate()]
            },
            expires_delta=timedelta(days=5))
        SQL('api_users').update(Record(session_token=user.session_token), f'id={user.id}')
        self.load()
        return user.session_token

    def is_session_token(self, data: Dict = None) -> bool:
        if data is None: data = get_jwt()
        return self.token_exists(data) and data.get('permissions') is not None

    def is_user_token(self, data: Dict = None) -> bool:
        if data is None: data = get_jwt()
        return self.token_exists(data) and data.get('permissions') is None

    def token_exists(self, data: Dict = None) -> bool:
        if data is None: data = get_jwt()
        return data.get("sub") is not None

    def verify(self, api: ApiNamespace) -> None:
        try:
            verify_jwt_in_request()
        except UserClaimsVerificationError:
            api.namespace.abort(code=403, message=session_manager.last_error)
        if current_user.id is None or current_user.id < 1:
            api.namespace.abort(code=403)


session_manager = SessionManager()

@session_manager._jwt_manager.user_identity_loader
def user_identity_loader(user: User) -> str:
    return str(user.id)

@session_manager._jwt_manager.user_lookup_loader
def user_lookup_loader(jwt_header: Any, jwt_data: Any) -> User:
    identity = jwt_data.get('sub')
    if identity is None: return None
    return session_manager.get_user_by_id(int(identity))

@session_manager._jwt_manager.token_verification_loader
def token_verification_loader(jwt_header: Any, jwt_data: Any) -> bool:
    def check(assertion: bool, message: str) -> bool:
        session_manager.last_error = message
        return assertion

    offset = 2 if request.path[-1] == '/' else 1
    request_endpoint = request.path.split('/')[-offset]
    if request_endpoint == 'session':
        if not check(session_manager.is_user_token(jwt_data), 'session token was passed to an endpoint requiring a user token.'):
            return False
    else:
        if not check(session_manager.is_session_token(jwt_data), 'user token was passed to an endpoint requiring a session token.'):
            return False
    return True