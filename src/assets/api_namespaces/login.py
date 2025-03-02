from os import getenv
from typing import Tuple
import requests
from api_server import ApiNamespace
from flask_restx import Resource, fields

from api_server.guild_manager import GuildManager
from api_server.login_manager import LoginManager

class LoginNamespace(ApiNamespace):
    def get_name(self) -> str:
        return 'login'

    def get_path(self) -> str:
        return 'login'

    def get_description(self) -> str:
        return 'Login endpoint.'

api = LoginNamespace()

LoginRequest = api.namespace.model('Login Request', {
    'code': fields.String(required=True, description='The discord application code.')
})

LoginResponse = api.namespace.model('Login Response', {
    'uuid': fields.String(required=True, description='The user api uuid.'),
    'name': fields.String(required=True, description='Username.')
})

@api.namespace.route('/')
class LoginRoute(Resource):
    @LoginManager.bind
    def login_manager(self) -> LoginManager: ...

    @api.namespace.expect(LoginRequest)
    @api.namespace.marshal_with(LoginResponse)
    def post(self):
        code = api.namespace.payload.get('code')
        code, message = self.discord_authenticate(code)
        if code < 1000:
            api.namespace.abort(code, message)
        user_id, user_name = code, message
        uuid = self.login_manager.set_user(user_id, user_name)
        GuildManager(uuid).load()
        return {'uuid': uuid, 'name': user_name}

    def discord_authenticate(self, code: str) -> Tuple[int, str]:
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
            user_id = json.get['id']
            name = json.get['username']
            if user_id is None or name is None: return 401, 'Unable to obtain user information.'
            return int(user_id), name
        return req.status_code, req.text