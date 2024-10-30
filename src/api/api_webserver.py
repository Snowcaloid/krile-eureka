

from abc import abstractmethod
from json import dumps
from typing import Dict, List, Any, Type
from discord import ChannelType
from flask import Flask, Request, request
from flask.views import View
from waitress import serve # type: ignore
from nullsafe import _
from uuid import UUID
from data.db.sql import SQL, Record
import bot
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType


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
    def request(self) -> Request: return request

    @property
    def webserver(self) -> ApiWebserver: return webserver

    def dispatch_request(self):
        if request.method == 'GET':
            if request.url_rule.rule.startswith('/api/post'):
                return self.post()
            return self.get()
        elif request.method == 'POST':
            return self.post()

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

@webserver.get('/api/channels')
def channels_get():
    user_uuid = request.args.get('user')
    if user_uuid is None: return [], 401
    user_cache = _(webserver.users_cache)[UUID(user_uuid)]
    if user_cache is None: return [], 401
    result = []
    for cached_guild in user_cache.guilds:
        data = {'guild': cached_guild['id'], 'channels': []}
        result.append(data)
        channels_data = bot.instance.data.guilds.get(cached_guild['id']).channels
        guild = bot.instance.get_guild(cached_guild['id'])
        for channel_data in channels_data.all:
            channel = guild.get_channel(channel_data.id)
            data['channels'].append({
                'id': channel_data.id,
                'name': _(channel).name,
                'function': channel_data.function.name,
                'event_type': channel_data.event_type})
    return result

@webserver.get('/api/post/channels')
def channels_post():
    user_uuid = request.args.get('user')
    if user_uuid is None: return [], 401
    user_cache = _(webserver.users_cache)[UUID(user_uuid)]
    if user_cache is None: return [], 401
    json = request.json
    for json_guild in _(json):
        guild_id = _(json_guild)['guild']
        if guild_id not in (guild["id"] for guild in user_cache.guilds):
            return f'Guild {_(json_guild)["guild"]} is not found in user cache for {user_cache.name}', 400
        guild_data = bot.instance.data.guilds.get(guild_id)
        guild = bot.instance.get_guild(guild_id)
        if guild is None: return f'Guild {guild_id} not found', 400
        for json_channel in _(json_guild)['channels']:
            channel_id = _(json_channel)['id']
            if channel_id is None: return f'Channel id is required for {dumps(json_channel)}', 400
            channel = guild.get_channel(channel_id)
            if channel is None: return f'Channel {channel_id} not found', 400
            if channel.type != ChannelType.text: return f'Channel {channel_id} is not a text channel', 400
            function = GuildChannelFunction[_(json_channel)['function']]
            event_type = _(json_channel)['event_type']
            channel_data = guild_data.channels.get(function, event_type)
            if channel_data is None:
                guild_data.channels.add(channel_id, function, event_type)
            elif _(json_channel)['delete']:
                guild_data.channels.remove(function, event_type)
            else:
                guild_data.channels.set(channel_id, function, event_type)
    return channels_get()

@webserver.get('/api/pings')
def pings_get():
    user_uuid = request.args.get('user')
    if user_uuid is None: return [], 401
    user_cache = _(webserver.users_cache)[UUID(user_uuid)]
    if user_cache is None: return [], 401
    result = []
    for cached_guild in user_cache.guilds:
        data = {'guild': cached_guild['id'], 'pings': []}
        result.append(data)
        pings_data = bot.instance.data.guilds.get(cached_guild['id']).pings
        guild = bot.instance.get_guild(cached_guild['id'])
        for ping_data in pings_data.all:
            role = guild.get_role(ping_data.tag)
            if role is None:
                user = guild.get_member(ping_data.tag)
            tag_type = 'role' if role is not None else 'user'
            tag_name = role.name if role is not None else _(user).display_name
            data['pings'].append({
                'id': ping_data.id,
                'tag_type': tag_type,
                'tag': ping_data.tag,
                'tag_name': tag_name,
                'type': ping_data.type.name,
                'event_type': ping_data.event_type})
    return result

@webserver.get('/api/post/pings')
def pings_post():
    user_uuid = request.args.get('user')
    if user_uuid is None: return [], 401
    user_cache = _(webserver.users_cache)[UUID(user_uuid)]
    if user_cache is None: return [], 401
    json = request.json
    for json_guild in _(json):
        guild_id = _(json_guild)['guild']
        if guild_id not in (guild["id"] for guild in user_cache.guilds):
            return f'Guild {_(json_guild)["guild"]} is not found in user cache for {user_cache.name}', 400
        guild_data = bot.instance.data.guilds.get(guild_id)
        guild = bot.instance.get_guild(guild_id)
        if guild is None: return f'Guild {guild_id} not found', 400
        for json_ping in _(json_guild)['pings']:
            ping_id = _(json_ping)['id']
            tag_type = _(json_ping)['tag_type']
            tag = _(json_ping)['tag']
            ping_type = GuildPingType[_(json_ping)['type']]
            event_type = _(json_ping)['event_type']
            if tag_type == 'role':
                role = guild.get_role(tag)
                if role is None: return f'Role {tag} not found', 400
            elif tag_type == 'user':
                user = guild.get_member(tag)
                if user is None: return f'User {tag} not found', 400
            else:
                return f'Invalid tag type {tag_type}', 400
            if not ping_id:
                guild_data.pings.add_ping(ping_type, event_type, tag)
            else:
                ping_data = guild_data.pings.get_by_id(id)
                if ping_data is None:
                    return f'Ping {ping_id} not found', 400
                elif _(json_ping)['delete']:
                    guild_data.pings.remove_by_id(ping_id)
                else:
                    guild_data.pings.set_by_id(ping_id, function, event_type, tag)
    return pings_get()

def run():
    webserver.load_users_cache()
    serve(webserver, port=6066)