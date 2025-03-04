from typing import Generator, override
from centralized_data import Singleton
from flask import Response
from flask_jwt_extended import current_user
from api_server import ApiNamespace
from flask_restx import Resource, fields
from discord.ext.commands import Bot

from api_server.permission_manager import PermissionManager
from data.db.sql import Transaction, in_transaction
from data.events.event import Event
from api_server.guild_manager import GuildManager
from data.events.event_templates import EventTemplates
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
    'type': fields.String(required=False, description='Event type descriptor.'),
    'guild_id': fields.String(required=False, description='Guild ID.'),
    'timestamp': fields.DateTime(required=False, description='Event timestamp.'),
    'description': fields.String(required=False, description='Event description.'),
    'raid_leader': fields.Nested(UserModel, required=False, description='Raid leader.'),
    'party_leaders': fields.List(fields.Nested(UserModel), required=False, description='Party leaders.'),
    'use_support': fields.Boolean(required=False, description='Use support.'),
    'pass_main': fields.Integer(required=False, description='Main passcode.'),
    'pass_supp': fields.Integer(required=False, description='Support passcode.'),
    'auto_passcode': fields.Boolean(required=False, description='Passcodes are handled by the bot.')
})

EventDeleteModel = api.namespace.model('Krile Event Cancellation', {
    'id': fields.Integer(required=True, description='Event ID.')
})

def _fetch_all_events() -> Generator[Event, None, None]:
    permissions = PermissionManager(current_user.id).calculate()
    for guild in GuildManager(current_user.id).all:
        allowed_categories = permissions[guild.id].raid_leading.categories
        for event in Schedule(guild.id).all:
            if event.category.value in allowed_categories:
                yield event

client = Singleton.get_instance(Bot)

def _username(user_id: int) -> str:
    if user_id is None or user_id < 1: return None
    return client.get_user(user_id).name

def _marshal(event: Event) -> dict:
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

@in_transaction
def _unmarshal(event: Event, m_event: dict):
    if 'type' in m_event:
        event.template = EventTemplates(event.guild_id).get(m_event['type'])
    if 'timestamp' in m_event:
        event.time = m_event['timestamp']
    if 'description' in m_event:
        event.real_description = m_event['description']
    if 'raid_leader' in m_event:
        event.users._raid_leader = m_event['raid_leader']['id']
    if 'party_leaders' in m_event:
        if len(m_event['party_leaders']) != 7:
            api.namespace.abort(400, 'Party leaders must be exactly 7.')
        event.users._party_leaders = [ leader['id'] for leader in m_event['party_leaders'] ]
    if 'use_support' in m_event:
        event.use_support = m_event['use_support']
    if 'auto_passcode' in m_event:
        event.auto_passcode = m_event['auto_passcode']

def _event_adjustable_by_user(event: Event) -> bool:
    permissions = PermissionManager(current_user.id).calculate()
    return event.category.value in permissions[event.guild_id].raid_leading.categories

def _get_event(event_id: int = None) -> Event:
    if event_id is None:
        event_id = api.namespace.payload.get("id")
        if event_id is None:
            api.namespace.abort(400)
    event = next((event for event in _fetch_all_events() if event.id == event_id), None)
    if event is None:
        api.namespace.abort(404)
    if not _event_adjustable_by_user(event):
        api.namespace.abort(403, 'Event not adjustable by user.')
    return event

@api.namespace.route('/')
class EventsRoute(Resource):
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(EventModel)
    def get(self):
        self.session_manager.verify(api)
        return [ _marshal(event) for event in _fetch_all_events() ]

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.expect(EventModel)
    @api.namespace.marshal_with(EventModel)
    def put(self):
        self.session_manager.verify(api)
        guild_id = api.namespace.payload.get("guild_id")
        if guild_id is None: api.namespace.abort(400, 'Guild ID is missing.')
        rl = api.namespace.payload.pop("raid_leader")
        if rl is None: api.namespace.abort(400, 'Raid leader is missing.')
        rl = rl.get("id")
        if rl is None: api.namespace.abort(400, 'Raid leader ID is missing.')
        event_type = api.namespace.payload.pop("type")
        if event_type is None: api.namespace.abort(400, 'Event type is missing.')
        event_type = EventTemplates(guild_id).get(event_type)
        if event_type is None: api.namespace.abort(400, 'Invalid event type.')
        time = api.namespace.payload.pop("timestamp")
        if time is None: api.namespace.abort(400, 'Event timestamp is missing.')
        Transaction()
        event = Schedule(int(guild_id)).add(rl, event_type, time)
        _unmarshal(event, api.namespace.payload)
        return _marshal(event)

@api.namespace.route('/<int:guild_id>')
class EventsRoute(Resource):
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.marshal_list_with(EventModel)
    def get(self, guild_id: int):
        self.session_manager.verify(api)
        return [ _marshal(event) for event in _fetch_all_events() if event.guild_id == guild_id ]

@api.namespace.route('/<int:event_id>')
class EventsRoute(Resource):
    from api_server.session_manager import SessionManager
    @SessionManager.bind
    def session_manager(self) -> SessionManager: ...

    @api.namespace.doc(security="jsonWebToken")
    @api.namespace.expect(EventModel)
    @api.namespace.marshal_with(EventModel)
    def patch(self, event_id: int):
        self.session_manager.verify(api)
        event = _get_event(event_id)
        _unmarshal(event, api.namespace.payload)
        return _marshal(event)

    @api.namespace.doc(security="jsonWebToken")
    def delete(self, event_id: int):
        self.session_manager.verify(api)
        event = _get_event(event_id)
        Schedule(event.guild_id).cancel(event.id)
        return Response(status=200)