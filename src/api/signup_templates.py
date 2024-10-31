

from nullsafe import _
from api.api_webserver import ApiRequest
import bot


class SignupTemplatesRequest(ApiRequest):
    """
    SignupTemplatesRequest API

    Endpoint:
        GET /api/signups

    Responses:
        200 OK:
        Description: Successfully retrieved the list of signup templates for each guild.
        Example:
            [
                {
                    "guild": 123456789012345678,
                    "signups": [
                        {
                            "id": 987654321098765432,
                            "owner": 876543210987654321,
                            "owner_name": "Owner",
                            "name": "Signup Template",
                            "description": "Description",
                            "short_description": "Short Description",
                            "event_category": "BA_CATEGORY",
                            "party_count": 5,
                            "use_support": true,
                            "recruitment_channel": 123456789012345678,
                            "use_passcodes": true,
                            "use_recruitment_posts": true,
                            "use_recruitment_post_thread": true,
                            "recruitment_post_thread_title": "%time %description",
                            "delete_recruitment_posts": true,
                            "recruitment_post_title": "%servertime %localtime %description",
                            "recruitment_post_text": "Recruitment Post Text",
                            "party_leader_dm_text": "%party %passcode",
                            "support_party_leader_dm_text": "%passcode",
                            "raid_leader_dm_text": "%passcode %support %passcode_support %support=%!support=",
                            "dm_title": "%servertime %localtime %description",
                            "dm_text": "%party %passcode",
                            "passcode_delay": 5,
                            "pl_button_texts": true,
                            "schedule_entry_text": "%servertime %localtime %rl %support %support=%!support=",
                            "slots": [
                                {
                                    "id": 1,
                                    "name": "Tank",
                                    "party": 1,
                                    "position": 1
                                }
                            ]
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
        POST /api/signups

    Request:
        [
            {
                "guild": 123456789012345678,
                "signups": [
                    {
                        "id": 987654321098765432,
                        "owner": 876543210987654321,
                        "name": "Signup Template",
                        "description": "Description",
                        "short_description": "Short Description",
                        "event_category": "BA_CATEGORY",
                        "party_count": 5,
                        "use_support": true,
                        "recruitment_channel": 123456789012345678,
                        "use_passcodes": true,
                        "use_recruitment_posts": true,
                        "use_recruitment_post_thread": true,
                        "recruitment_post_thread_title": "%time %description",
                        "delete_recruitment_posts": true,
                        "recruitment_post_title": "%servertime %localtime %description",
                        "recruitment_post_text": "Recruitment Post Text",
                        "party_leader_dm_text": "%party %passcode",
                        "support_party_leader_dm_text": "%passcode",
                        "raid_leader_dm_text": "%passcode %support %passcode_support %support=%!support=",
                        "dm_title": "%servertime %localtime %description",
                        "dm_text": "%party %passcode",
                        "passcode_delay": 5,
                        "pl_button_texts": true,
                        "schedule_entry_text": "%servertime %localtime %rl %support %support=%!support=",
                        "slots": [
                            {
                                "id": 1,
                                "name": "Tank",
                                "party": 1,
                                "position": 1,
                                "delete": true
                            }
                        ]
                    }
                ]
            }
        ]
    """
    @classmethod
    def route(cls): return 'signups'

    def get(self):
        user_cache, error = self.get_user_cache()
        if error: return error, 401
        result = []
        for cached_guild in user_cache.guilds:
            data = {'guild': cached_guild['id'], 'signups': []}
            result.append(data)
            guild = bot.instance.get_guild(cached_guild['id'])
            for signup_template in bot.instance.data.guilds.get(cached_guild['id']).signup_templates.all:
                slots = []
                for slot in signup_template.slots.all:
                    slots.append({
                        'id': slot.id,
                        'name': slot.name,
                        'party': slot.party,
                        'position': slot.position
                    })
                data['signups'].append({
                    'id': signup_template.id,
                    'owner': signup_template.owner,
                    'owner_name': _(guild.get_member(signup_template.owner)).display_name,
                    'name': signup_template.name,
                    'description': signup_template.description,
                    'short_description': signup_template.short_description,
                    'event_category': signup_template.event_category,
                    'party_count': signup_template.party_count,
                    'use_support': signup_template.use_support,
                    'recruitment_channel': signup_template.recruitment_channel,
                    'use_passcodes': signup_template.use_passcodes,
                    'use_recruitment_posts': signup_template.use_recruitment_posts,
                    'use_recruitment_post_thread': signup_template.use_recruitment_post_thread,
                    'recruitment_post_thread_title': signup_template.recruitment_post_thread_title,
                    'delete_recruitment_posts': signup_template.delete_recruitment_posts,
                    'recruitment_post_text': signup_template.recruitment_post_text,
                    'party_leader_dm_text': signup_template.party_leader_dm_text,
                    'support_party_leader_dm_text': signup_template.support_party_leader_dm_text,
                    'raid_leader_dm_text': signup_template.raid_leader_dm_text,
                    'dm_title': signup_template.dm_title,
                    'dm_text': signup_template.dm_text,
                    'passcode_delay': signup_template.passcode_delay,
                    'pl_button_texts': signup_template.pl_button_texts,
                    'schedule_entry_text': signup_template.schedule_entry_text,
                    'recruitment_post_title': signup_template.recruitment_post_title,
                    'slots': slots
                })
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
            for json_signup_template in _(json_guild)['signups']:
                signup_template_id = _(json_signup_template)['id']
                owner = _(json_signup_template)['owner']
                name = _(json_signup_template)['name']
                description = _(json_signup_template)['description']
                short_description = _(json_signup_template)['short_description']
                event_category = _(json_signup_template)['event_category']
                party_count = _(json_signup_template)['party_count']
                use_support = _(json_signup_template)['use_support']
                recruitment_channel = _(json_signup_template)['recruitment_channel']
                use_passcodes = _(json_signup_template)['use_passcodes']
                use_recruitment_posts = _(json_signup_template)['use_recruitment_posts']
                use_recruitment_post_thread = _(json_signup_template)['use_recruitment_post_thread']
                recruitment_post_thread_title = _(json_signup_template)['recruitment_post_thread_title']
                delete_recruitment_posts = _(json_signup_template)['delete_recruitment_posts']
                recruitment_post_text = _(json_signup_template)['recruitment_post_text']
                party_leader_dm_text = _(json_signup_template)['party_leader_dm_text']
                support_party_leader_dm_text = _(json_signup_template)['support_party_leader_dm_text']
                raid_leader_dm_text = _(json_signup_template)['raid_leader_dm_text']
                dm_title = _(json_signup_template)['dm_title']
                dm_text = _(json_signup_template)['dm_text']
                passcode_delay = _(json_signup_template)['passcode_delay']
                pl_button_texts = _(json_signup_template)['pl_button_texts']
                schedule_entry_text = _(json_signup_template)['schedule_entry_text']
                recruitment_post_title = _(json_signup_template)['recruitment_post_title']
                slots = _(json_signup_template)['slots']
                if not signup_template_id:
                    signup_template = guild_data.signup_templates.add(owner)
                else:
                    signup_template = guild_data.signup_templates.get(signup_template_id)
                    if signup_template is None:
                        return f'Signup Template {signup_template_id} not found', 400
                    elif _(json_signup_template)['delete']:
                        guild_data.signup_templates.remove(signup_template_id)
                        continue
                if owner: signup_template.owner = owner
                if name: signup_template.name = name
                if description: signup_template.description = description
                if short_description: signup_template.short_description = short_description
                if event_category: signup_template.event_category = event_category
                if party_count: signup_template.party_count = party_count
                if use_support: signup_template.use_support = use_support
                if recruitment_channel: signup_template.recruitment_channel = recruitment_channel
                if use_passcodes: signup_template.use_passcodes = use_passcodes
                if use_recruitment_posts: signup_template.use_recruitment_posts = use_recruitment_posts
                if use_recruitment_post_thread: signup_template.use_recruitment_post_thread = use_recruitment_post_thread
                if recruitment_post_thread_title: signup_template.recruitment_post_thread_title = recruitment_post_thread_title
                if delete_recruitment_posts: signup_template.delete_recruitment_posts = delete_recruitment_posts
                if recruitment_post_text: signup_template.recruitment_post_text = recruitment_post_text
                if party_leader_dm_text: signup_template.party_leader_dm_text = party_leader_dm_text
                if support_party_leader_dm_text: signup_template.support_party_leader_dm_text = support_party_leader_dm_text
                if raid_leader_dm_text: signup_template.raid_leader_dm_text = raid_leader_dm_text
                if dm_title: signup_template.dm_title = dm_title
                if dm_text: signup_template.dm_text = dm_text
                if passcode_delay: signup_template.passcode_delay = passcode_delay
                if pl_button_texts: signup_template.pl_button_texts = pl_button_texts
                if schedule_entry_text: signup_template.schedule_entry_text = schedule_entry_text
                if recruitment_post_title: signup_template.recruitment_post_title = recruitment_post_title
                for slot in slots:
                    slot_id = _(slot)['id']
                    name = _(slot)['name']
                    party = _(slot)['party']
                    position = _(slot)['position']
                    if not slot_id:
                        signup_template.slots.add(signup_template.id, name, party, position)
                    else:
                        slot = signup_template.slots.get(slot_id)
                        if slot is None:
                            return f'Slot {slot_id} not found', 400
                        elif _(slot)['delete']:
                            signup_template.slots.remove(slot_id)
                            continue
                    if name: slot.name = name
                    if party: slot.party = party
                    if position: slot.position = position
        return self.get()