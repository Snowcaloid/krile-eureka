

from typing import Dict, Tuple, Any
from flask import Flask, request
from waitress import serve # type: ignore
from nullsafe import _
from uuid import UUID, uuid4
import requests
import os
import bot


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

webserver = ApiWebserver()

def discord_authenticate(code: str) -> Tuple[int, str, Any]:
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

@webserver.get('/api/login')
def login():
    code = request.args.get('code')
    if code is None:
        uuid = request.args.get('uuid')
        if uuid is None:
            return { 'error': 'code or uuid is required' }, 400
    if code is None:
        return { 'uuid': uuid, 'name': webserver.users_cache[UUID(uuid)].name }
    else:
        user_id, name, error = discord_authenticate(code)
        if not error is None: return {'error': error}, 400
        uuid = uuid4()
        webserver.users_cache[uuid] = WebserverUserCache(uuid, name, user_id)
        return { 'uuid': str(uuid), 'name': name }

@webserver.get('/api/guilds')
def guilds_get():
    """Get all guilds for the user and cache them in the users_cache."""
    user_uuid = request.args.get('user')
    if user_uuid is None: return [], 401
    user_cache = _(webserver.users_cache)[UUID(user_uuid)]
    if user_cache is None: return [], 401
    user_id = user_cache.user_id
    user_cache.guilds.clear()
    result = []
    for guild_data in bot.instance.data.guilds.all:
        guild = bot.instance.get_guild(guild_data.id)
        user = guild.get_member(user_id)
        if user is None or not user.guild_permissions.administrator: continue
        result.append({'id': guild.id, 'name': guild.name})
    user_cache.guilds = result
    return result

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

@webserver.get('/api/roles')
def roles_get():
    user_uuid = request.args.get('user')
    if user_uuid is None: return [], 401
    user_cache = _(webserver.users_cache)[UUID(user_uuid)]
    if user_cache is None: return [], 401
    result = []
    for cached_guild in user_cache.guilds:
        data = {'guild': cached_guild['id'], 'roles': []}
        result.append(data)
        guild_data = bot.instance.data.guilds.get(cached_guild['id'])
        data['admin'] = {
            'id': guild_data.role_admin,
            'name': _(bot.instance.get_guild(cached_guild['id']).get_role(guild_data.role_admin)).name
        }
        data['developer'] = {
            'id': guild_data.role_developer,
            'name': _(bot.instance.get_guild(cached_guild['id']).get_role(guild_data.role_developer)).name
        }
        roles_data = bot.instance.data.guilds.get(cached_guild['id']).roles
        guild = bot.instance.get_guild(cached_guild['id'])
        for role_data in roles_data.all:
            role = guild.get_role(role_data.role_id)
            data['roles'].append({
                'id': role_data.role_id,
                'name': _(role).name,
                'function': role_data.function.name,
                'event_category': role_data.event_category})
    return result

def run():
    serve(webserver, port=6066)