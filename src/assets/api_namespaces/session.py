from typing import override
from flask import request
from flask_jwt_extended import get_jwt_identity
from api_server import ApiNamespace
from flask_restx import Resource, fields

from api_server.session_manager import SessionManager

class SessionNamespace(ApiNamespace):
    @override
    def get_name(self) -> str:
        return 'session'

    @override
    def get_path(self) -> str:
        return 'session'

    @override
    def get_description(self) -> str:
        return 'Grants user sessions.'

api = SessionNamespace()

Session = api.namespace.model('User session', {
    'token': fields.String(required=True, description='JWT token.')
})

@api.namespace.route('/')
class SessionRoute(Resource):
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_with(Session)
    def get(self):
        self.session_manager.verify(api)
        user_id = int(get_jwt_identity())
        if user_id is None or user_id < 1: api.namespace.abort(code=401, message='Invalid user token.')
        user = self.session_manager.get_user_by_id(user_id)
        if user is None: api.namespace.abort(code=401, message='User not found.')
        if user.user_token is None: api.namespace.abort(code=401, message='User is not logged in.')
        if not self.session_manager.is_user_token(): api.namespace.abort(code=403, message='Session Token cannot be used for session grants.')
        if not user.user_token in request.headers.get('Authorization'): api.namespace.abort(code=403, message='Invalid user token.')
        self.session_manager.open_session(user)
        return {
            'token': user.session_token
        }