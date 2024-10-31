

from typing import Any, Tuple
from nullsafe import _
from uuid import UUID, uuid4
from api.api_webserver import ApiRequest
import requests
import os


class LoginRequest(ApiRequest):
    """
    LoginRequest API

    Endpoint:
        GET /api/login

    Responses:
        200 OK:
        Description: Successfully authenticated the user.
        Example:
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "name": "Example User"
            }

        400 Bad Request:
        Description: Error authenticating the user.
        Example:
            {
                "error": "code or uuid is required"
            }
    """
    @classmethod
    def route(cls): return 'login'

    def get(self):
        req = self.request
        code = req.args.get('code')
        if code is None:
            uuid = req.args.get('uuid')
            if uuid is None:
                return { 'error': 'code or uuid is required' }, 400
        if code is None:
            return { 'uuid': uuid, 'name': self.webserver.users_cache[UUID(uuid)].name }
        else:
            user_id, name, error = self.discord_authenticate(code)
            if not error is None: return {'error': error}, 400
            uuid = uuid4()
            self.webserver.add_user_cache(uuid, name, user_id)
            return { 'uuid': str(uuid), 'name': name }


    def discord_authenticate(self, code: str) -> Tuple[int, str, Any]:
        """Authenticate the user with the Discord API."""
        req = requests.post('https://discord.com/api/oauth2/token',
                            headers={'Content-Type': 'application/x-www-form-urlencoded'},
                            data={
                                "client_id": os.getenv('WEBSERVER_CLIENT_ID'),
                                "client_secret": os.getenv('WEBSERVER_CLIENT_SECRET'),
                                "grant_type": "authorization_code",
                                "code": code,
                                "redirect_uri": os.getenv('WEBSERVER_REDIRECT_URI'),
                                "scope": "identify"
                            })
        if req.status_code != 200: return 0, '', {'status-code': req.status_code, 'error': req.text}
        json = req.json()
        req = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'{_(json)["token_type"]} {_(json)["access_token"]}'})
        if req.status_code == 200:
            json = req.json()
            user_id = _(json)['id']
            if user_id is None: return 0, '', {'status-code': 401, 'error': 'Unable to obtain user id.'}
            name = _(json)['username']
            return int(user_id), name, None
        return 0, '', {'status-code': req.status_code, 'error': req.text}
