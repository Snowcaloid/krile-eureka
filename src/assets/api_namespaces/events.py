from typing import Generator, override
from centralized_data import Singleton
from flask_jwt_extended import current_user
from api_server import ApiNamespace
from flask_restx import Resource, fields
from discord.ext.commands import Bot

from data.events.event import Event
from api_server.guild_manager import GuildManager
from data.events.schedule import Schedule

class EventsNamespace(ApiNamespace):
    @override
    def get_name(self) -> str:
        return 'events'

    @override
    def get_path(self) -> str:
        return 'events'

    @override
    def get_description(self) -> str:
        return 'Events management.'

    @override
    def use_jwt(self):
        return True

api = EventsNamespace()

UserModel = api.namespace.model('Simple User', {
    'id': fields.String(required=True, description='User ID.'),
    'name': fields.String(required=False, description='Username.')
})

EventModel = api.namespace.model('Krile Event', {
    'id': fields.Integer(required=False, description='Event ID.'),
    'type': fields.String(required=True, description='Event type descriptor.'),
    'guild_id': fields.String(required=True, description='Guild ID.'),
    'timestamp': fields.DateTime(required=True, description='Event timestamp.'),
    'description': fields.String(required=False, description='Event description.'),
    'raid_leader': fields.Nested(UserModel, required=True, description='Raid leader.'),
    'party_leaders': fields.List(fields.Nested(UserModel), required=False, description='Party leaders.'),
    'use_support': fields.Boolean(required=False, description='Use support.'),
    'pass_main': fields.Integer(required=False, description='Main pass.'),
    'pass_supp': fields.Integer(required=False, description='Support pass.')
})

def _fetch_all_events() -> Generator[Event, None, None]:
    for guild in GuildManager(current_user.id).all:
        for event in Schedule(guild.id).all:
            yield event

client = Singleton.get_instance(Bot)

def _username(user_id: int) -> str:
    if user_id is None or user_id < 1: return None
    return client.get_user(user_id).name

def marshal(event: Event) -> dict:
    return {
        "id": event.id,
        "type": event.template.type(),
        "guild_id": event.guild_id,
        "timestamp": event.time,
        "description": event.real_description,
        "raid_leader": {
            "id": event.users._raid_leader,
            "name": _username(event.users._raid_leader)
        },
        "party_leaders": [ {
            "id": leader,
            "name": _username(leader)
        } for leader in event.users._party_leaders ],
        "use_support": event.use_support,
        "pass_main": event.passcode_main,
        "pass_supp": event.passcode_supp
    }

@api.namespace.route('/')
class EventsRoute(Resource):
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(EventModel)
    def get(self):
        self.session_manager.verify(api)
        if current_user.id is None or current_user.id < 1: return []
        return [ marshal(event) for event in _fetch_all_events() ]

@api.namespace.route('/<int:guild_id>')
class EventsRoute(Resource):
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(EventModel)
    def get(self, guild_id: int):
        self.session_manager.verify(api)
        if current_user.id is None or current_user.id < 1: return []
        return [ marshal(event) for event in _fetch_all_events() if event.guild_id == guild_id ]

