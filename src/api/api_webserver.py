

from json import dumps
from typing import Dict, Tuple, Any
from discord import ChannelType
from flask import Flask, request
from waitress import serve # type: ignore
from nullsafe import _
from uuid import UUID, uuid4
from data.db.sql import SQL, Record
import requests
import os
import bot
from data.guilds.guild_channel_functions import GuildChannelFunction
from data.guilds.guild_pings import GuildPingType
from data.guilds.guild_role_functions import GuildRoleFunction


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
        webserver.add_user_cache(uuid, name, user_id)
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

@webserver.get('/api/post/roles')
def roles_post():
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
        admin_role = _(json_guild)['admin']
        if not admin_role is None:
            guild_data.role_admin = admin_role
        developer_role = _(json_guild)['developer']
        if not developer_role is None:
            guild_data.role_developer = developer_role
        for json_role in _(json_guild)['roles']:
            role_id = _(json_role)['id']
            function = GuildRoleFunction[_(json_role)['function']]
            event_category = _(json_role)['event_category']
            role = guild.get_role(role_id)
            if role is None: return f'Role {role_id} not found', 400
            role_data = guild_data.roles.get(function, event_category)
            if not role_data:
                guild_data.roles.add(role_id, function, event_category)
            elif _(json_role)['delete']:
                guild_data.roles.remove(role_id, function, event_category)
            else:
                guild_data.roles.set(role_id, function, event_category)
    return roles_get()

def run():
    webserver.load_users_cache()
    serve(webserver, port=6066)