

from nullsafe import _
from api.api_webserver import ApiRequest
import bot
from data.guilds.guild_role_functions import GuildRoleFunction


class RolesRequest(ApiRequest):
    """
    RolesRequest API

    Endpoint:
        GET /api/roles

    Responses:
        200 OK:
        Description: Successfully retrieved the list of roles for each guild.
        Example:
            [
                {
                    "guild": 123456789012345678,
                    "admin": {
                        "id": 987654321098765432,
                        "name": "Admin"
                    },
                    "developer": {
                        "id": 876543210987654321,
                        "name": "Developer"
                    },
                    "roles": [
                        {
                            "id": 987654321098765432,
                            "name": "BA Raid Leader",
                            "function": "RAID_LEADER",
                            "event_category": "BA_CATEGORY"
                        },
                        {
                            "id": 876543210987654321,
                            "name": "DRS Raid Leader",
                            "function": "RAID_LEADER",
                            "event_category": "DRS_CATEGORY"
                        }
                    ]
                }
            ]

        401 Unauthorized:
        Description: Error retrieving the user cache.
        Example:
            {
                "error": "Unauthorized access"
            }

    Endpoint:
        POST /api/roles

    Request:
        [
            {
                "guild": 123456789012345678,
                "admin": 987654321098765432,
                "developer": 876543210987654321,
                "roles": [
                    {
                        "id": 987654321098765432,
                        "function": "RAID_LEADER",
                        "event_category": "BA_CATEGORY",
                        "delete": true
                    },
                    {
                        "id": 876543210987654321,
                        "function": "RAID_LEADER",
                        "event_category": "DRS_CATEGORY",
                        "delete": false
                    }
                ]
            }
        ]
    """

    @classmethod
    def route(cls): return 'roles'

    def get(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
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

    def post(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
        json = self.request.json
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
        return self.get()
