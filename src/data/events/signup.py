

from typing import List, Tuple
from data.db.sql import SQL, Record

class SignupTemplateSlot:
    def __init__(self, id: int, name: str, party: int, position: int):
        self.id = id
        self.name = name
        self.party = party
        self.position = position

class SignupTemplateSlots:
    _list: List[SignupTemplateSlot]

    def __init__(self):
        self._list = []

    def load(self, signup_template_id: int):
        self._list.clear()
        for record in SQL('signup_template_slots').select(fields=['id', 'name', 'party', 'position'],
                                                          where=f'template_id={signup_template_id}',
                                                          all=True,
                                                          sort_fields=['party', 'position']):
            self._list.append(SignupTemplateSlot(record['id'], record['name'], record['party'], record['position']))

    def get(self, slot_id: int) -> SignupTemplateSlot:
        return next((slot for slot in self._list if slot.id == slot_id), None)

    def for_party(self, party: int) -> List[SignupTemplateSlot]:
        return [slot for slot in self._list if slot.party == party]

    def add(self, signup_template_id: int, name: str, party: int, position: int) -> SignupTemplateSlot:
        id = SQL('signup_template_slots').insert(Record(template_id=signup_template_id,
                                                        name=name,
                                                        party=party,
                                                        position=position),
                                                 returning_field='id')
        self.load(self.id)
        return self.get(id)

    def remove(self, slot_id: int) -> None:
        SQL('signup_template_slots').delete(f'id={slot_id}')
        self.load(self.id)

    @property
    def all(self) -> List[SignupTemplateSlot]:
        return self._list

class SignupTemplate:
    id: int
    slots: SignupTemplateSlots
    guild_id: int
    _owner: int
    _name: str
    _event_category: str
    _party_count: int
    _use_support: bool
    _recruitment_channel: int
    _description: str
    _short_description: str
    _use_passcodes: bool
    _use_recruitment_posts: bool
    _use_recruitment_post_thread: bool
    _recruitment_post_thread_title: str
    _delete_recruitment_posts: bool
    _recruitment_post_text: str
    _party_leader_dm_text: str
    _support_party_leader_dm_text: str
    _raid_leader_dm_text: str
    _dm_title: str
    _dm_text: str
    _passcode_delay: int
    _pl_button_texts: Tuple[str, str, str, str, str, str, str]
    _schedule_entry_text: str
    _recruitment_post_title: str

    def __init__(self):
        self.slots = SignupTemplateSlots()
        self._event_category = 'CUSTOM_CATEGORY'
        self._party_count = 6
        self._use_support = False
        self._recruitment_channel = 0
        self._description = 'Custom Signup Run'
        self._short_description = 'Custom Run'
        self._use_passcodes = True
        self._use_recruitment_posts = True
        self._use_recruitment_post_thread = False
        self._recruitment_post_thread_title = '%time %description'
        self._delete_recruitment_posts = True
        self._recruitment_post_title = '%servertime ST (%localtime LT) %description Recruitment'
        self._recruitment_post_text = 'To sign up for the run, use the interactive components below.'
        self._party_leader_dm_text = (
            f'You\'re leading party %party.\n'
            f'[SoB] Custom Signup Run party %party\n'
            f'Passcode is **%passcode**.'
        )
        self._support_party_leader_dm_text = (
            'You\'re leading **the support party.**\n'
            '[SoB] Custom Signup Run support party\n'
            f'Passcode is **%passcode**.'
        )
        self._raid_leader_dm_text = (
            f'Passcode for the Alliance will be: **%passcode**\n'
            '%support'
            'These passcode(s) have been sent to the relevant party leaders.\n'
            'The passcode(s) will be posted automatically at the appropriate time for that run.\n'
            '%support=Passcode for the Support Party will be: **%passcode_support**\n'
            '%!support=Support party has been excluded manually by the raid leader. The support passcode will not be posted. In case this is changed, the passcode is **%passcode_support**.\n'
        )
        self._dm_title = '%servertime ST (%localtime LT) %description Passcode Notification'
        self._dm_text = (
            'Please open Adventuring Forays Tab in the Private Party Finder section and join the party with the passcode provided.\n\n'
            f'Your party is **party %party**.\n'
            f'The passcode is **%passcode**.\n\n'
            'Please make sure to be prepared for the run.\n'
            'If you have any questions, please ask the raid leader or party leader.\n'
            '**Make sure that you enter the party before the run starts.**'
        )
        self._passcode_delay = 15
        self._pl_button_texts = '1', '2', '3', '4', '5', '6', 'Support'
        self._schedule_entry_text = (
            '**%servertime ST (%localtime LT)**: Custom Signup Run (%rl)%support\n'
            '%support=\n'
            '%!support=(__no support__)'
        )

    def load(self, signup_template_id: int):
        record = SQL('signup_templates').select(fields=['guild_id', 'owner', 'name', 'event_category',
                                                 'party_count', 'use_support', 'recruitment_channel',
                                                 'description', 'short_description',
                                                 'use_passcodes', 'use_recruitment_posts',
                                                 'use_recruitment_post_thread', 'recruitment_post_thread_title',
                                                 'delete_recruitment_posts', 'recruitment_post_text',
                                                 'party_leader_dm_text', 'support_party_leader_dm_text',
                                                 'raid_leader_dm_text', 'dm_text', 'passcode_delay',
                                                 'pl_button_texts', 'schedule_entry_text',
                                                 'recruitment_post_title', 'dm_title'],
                                                where=f'id={signup_template_id}')
        if record:
            self.id = signup_template_id
            self.guild_id = record['guild_id']
            self._owner = record['owner']
            self._name = record['name']
            self._event_category = record['event_category']
            self._party_count = record['party_count']
            self._use_support = record['use_support']
            self._recruitment_channel = record['recruitment_channel']
            self._description = record['description']
            self._short_description = record['short_description']
            self._use_passcodes = record['use_passcodes']
            self._use_recruitment_posts = record['use_recruitment_posts']
            self._use_recruitment_post_thread = record['use_recruitment_post_thread']
            self._recruitment_post_thread_title = record['recruitment_post_thread_title']
            self._delete_recruitment_posts = record['delete_recruitment_posts']
            self._recruitment_post_text = record['recruitment_post_text']
            self._recruitment_post_title = record['recruitment_post_title']
            self._party_leader_dm_text = record['party_leader_dm_text']
            self._support_party_leader_dm_text = record['support_party_leader_dm_text']
            self._raid_leader_dm_text = record['raid_leader_dm_text']
            self._dm_title = record['dm_title']
            self._dm_text = record['dm_text']
            self._passcode_delay = record['passcode_delay']
            if record['pl_button_texts']:
                self._pl_button_texts = tuple(record['pl_button_texts'])
            self._schedule_entry_text = record['schedule_entry_text']
            self.slots.load(signup_template_id)

    @property
    def owner(self) -> int:
        return self._owner

    @owner.setter
    def owner(self, value: int) -> None:
        SQL('signup_templates').update(Record(owner=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        SQL('signup_templates').update(Record(name=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def event_category(self) -> str:
        return self._event_category

    @event_category.setter
    def event_category(self, value: str) -> None:
        SQL('signup_templates').update(Record(event_category=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def party_count(self) -> int:
        return self._party_count

    @party_count.setter
    def party_count(self, value: int) -> None:
        SQL('signup_templates').update(Record(party_count=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def use_support(self) -> bool:
        return self._use_support

    @use_support.setter
    def use_support(self, value: bool) -> None:
        SQL('signup_templates').update(Record(use_support=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def recruitment_channel(self) -> int:
        return self._recruitment_channel

    @recruitment_channel.setter
    def recruitment_channel(self, value: int) -> None:
        SQL('signup_templates').update(Record(recruitment_channel=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        SQL('signup_templates').update(Record(description=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def short_description(self) -> str:
        return self._short_description

    @short_description.setter
    def short_description(self, value: str) -> None:
        SQL('signup_templates').update(Record(short_description=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def use_passcodes(self) -> bool:
        return self._use_passcodes

    @use_passcodes.setter
    def use_passcodes(self, value: bool) -> None:
        SQL('signup_templates').update(Record(use_passcodes=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def use_recruitment_posts(self) -> bool:
        return self._use_recruitment_posts

    @use_recruitment_posts.setter
    def use_recruitment_posts(self, value: bool) -> None:
        SQL('signup_templates').update(Record(use_recruitment_posts=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def use_recruitment_post_thread(self) -> bool:
        return self._use_recruitment_post_thread

    @use_recruitment_post_thread.setter
    def use_recruitment_post_thread(self, value: bool) -> None:
        SQL('signup_templates').update(Record(use_recruitment_post_thread=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def recruitment_post_thread_title(self) -> str:
        return self._recruitment_post_thread_title

    @recruitment_post_thread_title.setter
    def recruitment_post_thread_title(self, value: str) -> None:
        SQL('signup_templates').update(Record(recruitment_post_thread_title=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def delete_recruitment_posts(self) -> bool:
        return self._delete_recruitment_posts

    @delete_recruitment_posts.setter
    def delete_recruitment_posts(self, value: bool) -> None:
        SQL('signup_templates').update(Record(delete_recruitment_posts=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def recruitment_post_text(self) -> str:
        return self._recruitment_post_text

    @recruitment_post_text.setter
    def recruitment_post_text(self, value: str) -> None:
        SQL('signup_templates').update(Record(recruitment_post_text=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def recruitment_post_title(self) -> str:
        return self._recruitment_post_title

    @recruitment_post_title.setter
    def recruitment_post_title(self, value: str) -> None:
        SQL('signup_templates').update(Record(recruitment_post_title=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def party_leader_dm_text(self) -> str:
        return self._party_leader_dm_text

    @party_leader_dm_text.setter
    def party_leader_dm_text(self, value: str) -> None:
        SQL('signup_templates').update(Record(party_leader_dm_text=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def support_party_leader_dm_text(self) -> str:
        return self._support_party_leader_dm_text

    @support_party_leader_dm_text.setter
    def support_party_leader_dm_text(self, value: str) -> None:
        SQL('signup_templates').update(Record(support_party_leader_dm_text=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def raid_leader_dm_text(self) -> str:
        return self._raid_leader_dm_text

    @raid_leader_dm_text.setter
    def raid_leader_dm_text(self, value: str) -> None:
        SQL('signup_templates').update(Record(raid_leader_dm_text=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def dm_text(self) -> str:
        return self._dm_text

    @dm_text.setter
    def dm_text(self, value: str) -> None:
        SQL('signup_templates').update(Record(dm_text=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def dm_title(self) -> str:
        return self._dm_title

    @dm_title.setter
    def dm_title(self, value: str) -> None:
        SQL('signup_templates').update(Record(dm_title=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def passcode_delay(self) -> int:
        return self._passcode_delay

    @passcode_delay.setter
    def passcode_delay(self, value: int) -> None:
        SQL('signup_templates').update(Record(passcode_delay=value),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def pl_button_texts(self) -> Tuple[str, str, str, str, str, str, str]:
        return self._pl_button_texts

    @pl_button_texts.setter
    def pl_button_texts(self, value: Tuple[str, str, str, str, str, str, str]) -> None:
        SQL('signup_templates').update(Record(pl_button_texts=list(value)),
                                       f'id={self.id}')
        self.load(self.id)

    @property
    def schedule_entry_text(self) -> str:
        return self._schedule_entry_text

    @schedule_entry_text.setter
    def schedule_entry_text(self, value: str) -> None:
        SQL('signup_templates').update(Record(schedule_entry_text=value),
                                       f'id={self.id}')
        self.load(self.id)


class SignupSlot:
    template: SignupTemplateSlot
    user_id: int
    id: int

    def __init__(self, id: int, template: SignupTemplateSlot, user_id: int):
        self.id = id
        self.template = template
        self.user_id = user_id

class SignupSlots:
    _list: List[SignupSlot]
    signup_id: int
    template: SignupTemplate

    def __init__(self):
        self._list = []

    def load(self, signup_id: int, template: SignupTemplate):
        self._list.clear()
        self.signup_id = signup_id
        self.template = template
        for record in SQL('signup_slots').select(fields=['id', 'template_id', 'user_id'],
                                            where=f'signup_id={signup_id}',
                                            all=True):
            self._list.append(SignupSlot(template.slots.get(record['id'], record['template_id']), record['user_id']))

    def get(self, template: SignupTemplateSlot) -> SignupSlot:
        return next((slot for slot in self._list if slot.template == template), None)

    def find(self, user_id: int) -> SignupSlot:
        return next((slot for slot in self._list if slot.user_id == user_id), None)

    def add(self, template: SignupTemplateSlot, user_id: int) -> SignupSlot:
        SQL('signup_slots').insert(Record(template_id=template,
                                          signup_id=self.signup_id,
                                          user_id=user_id))
        self.load(self.signup_id, self.template)
        return self.get(template)

    def remove(self, id: int) -> None:
        SQL('signup_slots').delete(f'id={id}')
        self.load(self.signup_id, self.template)

    @property
    def all(self):
        return self._list

class Signup:
    id: int
    template: SignupTemplate
    slots: SignupSlots

    def __init__(self):
        self.template = SignupTemplate()
        self.slots = SignupSlots()

    def load(self, signup_id: int):
        if signup_id is None: return
        record = SQL('signups').select(fields=['template_id'], where=f'id={signup_id}')
        if record:
            self.id = signup_id
            self.template.load(record['template_id'])
