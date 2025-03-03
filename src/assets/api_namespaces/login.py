from os import getenv
from typing import Tuple, override
import requests
from api_server import ApiNamespace
from flask_restx import Resource, fields

from api_server.session_manager import SessionManager

class LoginNamespace(ApiNamespace):
    @override
    def get_name(self) -> str:
        return 'login'

    @override
    def get_path(self) -> str:
        return 'login'

    @override
    def get_description(self) -> str:
        return 'Login endpoint.'

api = LoginNamespace()

LoginRequest = api.namespace.model('Login Request', {
    'code': fields.String(required=False, description='The discord application code.')
})

LoginResponse = api.namespace.model('Login Response', {
    'token': fields.String(required=True, description='JWT token.'),
    'id': fields.Integer(required=True, description='User ID.'),
    'name': fields.String(required=False, description='Username.')
})

@api.namespace.route('/')
class LoginRoute(Resource):
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.expect(LoginRequest)
    @api.namespace.marshal_with(LoginResponse)
    def post(self):
        code = api.namespace.payload.get('code')
        code, message = self.discord_identify(code)
        if code < 1000:
            api.namespace.abort(code, message)
        user_id, user_name = code, message
        user = self.session_manager.get_user_by_id(user_id)
        if user is None:
            user = self.session_manager.add_user(user_id, user_name)
        self.session_manager.login(user)
        return {
            'token': user.user_token,
            'id': user.id,
            'name': user.name
        }

    def discord_identify(self, code: str) -> Tuple[int, str]:
        """Authenticate the user with the Discord API."""
        req = requests.post('https://discord.com/api/oauth2/token',
                            headers={'Content-Type': 'application/x-www-form-urlencoded'},
                            data={
                                "client_id": getenv('WEBSERVER_CLIENT_ID'),
                                "client_secret": getenv('WEBSERVER_CLIENT_SECRET'),
                                "grant_type": "authorization_code",
                                "code": code,
                                "redirect_uri": getenv('WEBSERVER_REDIRECT_URI'),
                                "scope": "identify"
                            })
        if req.status_code != 200: return req.status_code, req.text
        json = req.json()
        req = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'{json.get("token_type")} {json.get("access_token")}'})
        if req.status_code == 200:
            json = req.json()
            user_id = json.get('id')
            name = json.get('username')
            if user_id is None or name is None: return 401, 'Unable to obtain user information.'
            return int(user_id), name
        return req.status_code, req.text