

from abc import abstractmethod
from copy import deepcopy
from typing import Dict, List, Any, Tuple, Type
from flask import Flask, Request, request
from flask.views import View
from waitress import serve # type: ignore
from nullsafe import _
from uuid import UUID
from data.db.sql import SQL, Record


class WebserverUserCache:
    def __init__(self, uuid: UUID, name: str, user_id: int):
        self.user_id = user_id
        self.guilds = []
        self.uuid = uuid
        self.name = name

class WebserverUsersCache(Dict[UUID, WebserverUserCache]): pass

class ApiWebserver(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__('krile_backend', *args, **kwargs)
        self.users_cache = WebserverUsersCache()

    def get_user_by_token(self, token: str) -> WebserverUserCache:
        return next((cache_item for cache_item in self.users_cache if cache_item.token == token), None)

    def load_users_cache(self) -> None:
        self.users_cache.clear()
        for record in SQL('webserver_users').select(fields=['uuid', 'user_id', 'user_name']):
            self.users_cache[UUID(record['uuid'])] = WebserverUserCache(UUID(record['uuid']), record['user_name'], record['user_id'])

    def add_user_cache(self, uuid: UUID, name: str, user_id: int):
        SQL('webserver_users').delete(f"user_id = {user_id}")
        SQL('webserver_users').insert(Record(uuid=str(uuid), user_id=user_id, user_name=name))
        self.load_users_cache()

webserver = ApiWebserver()

class ApiRequest(View):
    @classmethod
    def route(cls) -> str: pass

    @classmethod
    def base_url(cls) -> str: return '/api'

    @classmethod
    def url(cls) -> str: return f'{cls.base_url()}/{cls.route()}'

    @property
    def request(self) -> Request: return self._request

    @property
    def webserver(self) -> ApiWebserver: return webserver

    def dispatch_request(self):
        self._request = deepcopy(request)
        if request.method == 'GET':
            if request.url_rule.rule.startswith('/api/post'):
                return self.post()
            return self.get()
        elif request.method == 'POST':
            return self.post()

    def get_user_cache(self) -> Tuple[WebserverUserCache, str]:
        user_uuid = self.request.args.get('user')
        if user_uuid is None: return None, 'user parameter not found'
        user_cache = _(self.webserver.users_cache)[UUID(user_uuid)]
        if user_cache is None: return None, 'invalid user'
        return user_cache, ''

    @abstractmethod
    def get(self) -> Any: pass

    def post(self) -> Any:
        return 'Forbidden', 403

class ApiRequestRegister:
    HANDLERS: List[Type[ApiRequest]] = []

    @classmethod
    def register(cls, request_type: Type[ApiRequest]) -> None:
        webserver.add_url_rule(request_type.url(),
                               view_func=request_type.as_view(
                                   f'{request_type.url()}_get'),
                               methods=['GET'])
        webserver.add_url_rule(f'{request_type.base_url()}/post/{request_type.route()}',
                               view_func=request_type.as_view(
                                   f'{request_type.url()}_post'),
                               methods=['GET']) # TODO: replace post when testing is done
        cls.HANDLERS.append(request_type)

def run():
    webserver.load_users_cache()
    serve(webserver, port=6066)