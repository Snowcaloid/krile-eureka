
from datetime import datetime, timedelta
from enum import Enum
from json import dumps
from os import path, walk
from typing import List, Tuple
from discord.app_commands import Choice
import yaml

from utils import get_discord_timestamp


class EventCategory(Enum):
    CUSTOM = 'CUSTOM_CATEGORY'
    BA = 'BA_CATEGORY'
    DRS = 'DRS_CATEGORY'
    BOZJA = 'BOZJA_CATEGORY'
    CHAOTIC = 'CHAOTIC'

    @classmethod
    def all_category_choices(cl) -> List[Choice]:
        return [
            Choice(name='Custom runs', value=cl.CUSTOM.value),
            Choice(name='All BA runs', value=cl.BA.value),
            Choice(name='All DRS runs', value=cl.DRS.value),
            Choice(name='All Bozja-related runs', value=cl.BOZJA.value),
            Choice(name='All Chaotic Alliance runs', value=cl.CHAOTIC.value)
        ]

    @classmethod
    def all_category_choices_short(cl) -> List[Choice]:
        return [
            Choice(name='Custom run', value=cl.CUSTOM.value),
            Choice(name='BA', value=cl.BA.value),
            Choice(name='DRS', value=cl.DRS.value),
            Choice(name='Bozja', value=cl.BOZJA.value),
            Choice(name='Chaotic', value=cl.CHAOTIC.value)
        ]

class EventTemplate:
    _source: object = None

    def __init__(self, source: object):
        self._source = source

    @property
    def data(self) -> str:
        return dumps(self._source)

    #TODO: Refactor
    # def all_events_for_category(self, category: EventCategory) -> List[Type['Event']]:
    #     return [event_base for event_base in Event._registered_events if event_base.category() == category]

    # def all_choices_for_category(self, category: EventCategory) -> List[Choice]:
    #     return [event_base.as_choice() for event_base in Event.all_events_for_category(category)]

    # def all_types(self) -> List[str]:
    #     return [event_base.type() for event_base in Event._registered_events]

    # def by_type(self, type: str) -> Type['Event']:
    #     return next((event_base for event_base in Event._registered_events if event_base.type() == type), Event)

    def _handle_support_text(self, use_support: bool, template_text: str) -> str:
        index_of_no_support = template_text.find('%!support=') if '%!support=' in template_text else -1
        no_support_text = template_text[index_of_no_support + len('%!support='):] if '%!support=' in template_text else ''
        if index_of_no_support = -1:
            support_text = template_text[template_text.find('%support=') + len('%support='):] if '%support=' in template_text else ''
        else:
            support_text = template_text[template_text.find('%support=') + len('%support='):template_text.find('%!support=')] if '%support=' in template_text else ''

        if self.use_support() and use_support:
            return template_text.replace('%support', support_text)
        else:
            return template_text.replace('%support', no_support_text)

    def type(self) -> str:
        return self._source.get('type', 'CUSTOM')

    def description(self) -> str:
        return self._source.get('description', 'Custom run')

    def short_description(self) -> str:
        return self._source.get('short_description', 'Custom run')

    def category(self) -> EventCategory:
        return EventCategory(self._source.get('category', 'CUSTOM_CATEGORY'))

    def use_pl_posts(self) -> bool:
        return self._source.get('use_pl_posts', False)

    def use_passcodes(self) -> bool:
        return self._source.get('use_passcodes', False)

    def recruitment_post_title(self, time: datetime) -> str:
        value = self._source.get('recruitment_post_title', (
            '%time ST (%localtime LT): %description Party Leader Recruitment'
        ))
        return value.replace('%time', time.strftime(f"%A, %d-%b-%y %H:%M ST")).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', self.description())

    def recruitment_post_text(self,
                              rl: str, pl1: str, pl2: str, pl3: str,
                              pl4: str, pl5: str, pl6: str, pls: str,
                              use_support: bool) -> str:
        value = self._source.get('recruitment_post_text', (
            f'Raid Leader: %rl\n'
            f'1: %pl1\n'
            f'2: %pl2\n'
            f'3: %pl3\n'
            f'4: %pl4\n'
            f'5: %pl5\n'
            f'6: %pl6\n'
            f'%support\n'
            'Please note, your assignment may be removed at the Raid Leader\'s discretion.\n'
            '%support=Support: %pls\n'
            '%!support=Support party has been excluded manually by the raid leader.\n'
        ))
        value = self._handle_support_text(use_support, value)

        return value.replace('%rl', rl).replace('%pl1', pl1).replace('%pl2', pl2).replace('%pl3', pl3).replace(
            '%pl4', pl4).replace('%pl5', pl5).replace('%pl6', pl6).replace('%pls', pls)

    def pl_button_texts(self) -> Tuple[str, str, str, str, str, str, str]:
        list = self._source.get('pl_button_texts', ['1', '2', '3', '4', '5', '6', 'Support'])
        if len(list) < 7: list = list + [''] * (7 - len(list)) # Fill up with empty strings
        return tuple(list)

    def use_recruitment_post_threads(self) -> bool:
        return self._source.get('use_recruitment_post_threads', False)

    def delete_recruitment_posts(self) -> bool:
        return self._source.get('delete_recruitment_posts', True)

    def recruitment_post_thread_title(self, time: datetime) -> str:
        value = self._source.get('recruitment_post_thread_title', f'%time {self.description()}')
        return value.replace('%time', time.strftime('%A, %d %B %Y'))

    def use_support(self) -> bool:
        return self._source.get('use_support', False)

    def main_passcode_text(self, rl: str, passcode: int) -> str:
        value = self._source.get('main_passcode_text',(
            f'Raid Leader: %rl.\n\n'
            f'**The passcode for all Parties is **%passcode.**\n'
            'This will not work for the Support Party.\n\n'
            'Notes:\n'
            '1: Please bring proper logograms. If you do not bring and use Spirit of the Remembered we will not revive you.\n'
            '2: We can not revive players normally in BA, so please bear this in mind and do mechanics properly.\n'
            '3: If you die on trash mobs, this will usually result in you not being revived. There is no reason to die on them, so please wait 5s for the tank to establish aggro.'
        ))
        return value.replace('%rl', rl).replace('%passcode', str(passcode).zfill(4))

    def support_passcode_text(self, rl: str, passcode: int) -> str:
        value = self._source.get('support_passcode_text', (
            f'Raid Leader: %rl.\n\n'
            f'**The Support Party passcode is **%passcode.**\n\n'
            'Notes:\n'
            '1: Please bring proper logograms. If you do not bring and use Spirit of the Remembered we will not revive you.\n'
            '2: We can not revive players normally in BA, so please bear this in mind and do mechanics properly.\n'
            '3: If you die on trash mobs, this will usually result in you not being revived. There is no reason to die on them, so please wait 5s for the tank to establish aggro.'
        ))
        return value.replace('%rl', rl).replace('%passcode', str(passcode).zfill(4))

    def dm_title(self, time: datetime) -> str:
        value = self._source.get('dm_title', (
            '%time ST (%localtime LT) %description Passcode Notification'
        ))
        return value.replace('%time', time.strftime(f"%A, %d-%b-%y %H:%M ST")).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', self.description())

    def party_leader_dm_text(self, party: str, passcode: int) -> str:
        value = self._source.get('party_leader_dm_text', (
            f'You\'re leading **party %party.**\n'
            f'Passcode is **%passcode**.'
        ))
        return value.replace('%party', party).replace('%passcode', str(passcode).zfill(4))

    def support_party_leader_dm_text(self, passcode: int) -> str:
        value = self._source.get('support_party_leader_dm_text', (
            'You\'re leading **the support party.**\n'
            f'Passcode is **%passcode**.'
        ))
        return value.replace('%passcode', str(passcode).zfill(4))

    def raid_leader_dm_text(self, passcode_main: int, passcode_supp: int, use_support: bool) -> str:
        value = self._source.get('raid_leader_dm_text', (
            f'Passcode for all parties will be: **%passcode_main**\n'
            '%support\n'
            'These passcode(s) have been sent to the relevant party leaders.\n'
            'The passcode(s) will be posted automatically at the appropriate time for that run.'
            '%support=Passcode for the Support Party will be: **%passcode_support**\n'
            '%!support=Support party has been excluded manually by the raid leader. The support passcode will not be posted. In case this is changed, the passcode is **%passcode_support**.'
        ))
        value = self._handle_support_text(use_support, value)
        return value.replace('%passcode_main', str(passcode_main).zfill(4)).replace('%passcode_support', str(passcode_supp).zfill(4))

    def pl_passcode_delay(self) -> timedelta:
        return timedelta(minutes=self._source.get('pl_passcode_delay', 30))

    def support_passcode_delay(self) -> timedelta:
      return timedelta(minutes=self._source.get('support_passcode_delay', 20))

    def main_passcode_delay(self) -> timedelta:
        return timedelta(minutes=self._source.get('main_passcode_delay', 15))

    def schedule_entry_text(self, rl: str, time: datetime, custom: str, use_support: bool) -> str:
        value = self._source.get('schedule_entry_text', (
            '(%time ST (%localtime LT)): %description (%rl)%support%!support= __(No support)__'
        ))
        value = self._handle_support_text(use_support, value)
        return value.replace('%time', time.strftime('%H:%M')).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', custom).replace('%rl', rl)

    def passcode_post_title(self, time: datetime) -> str:
        value = self._source.get('passcode_post_title', (
            '%time ST (%localtime LT): %description Passcode'
        ))
        return value.replace('%time', time.strftime(f"%A, %d-%b-%y %H:%M ST")).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', self.description())

    def is_signup(self) -> bool:
        return self._source.get('is_signup', False)

    def as_choice(self) -> Choice:
        return Choice(name=self.description(), value=self.type())


class DefaultEventTemplates:
    _list: List[EventTemplate] = []

    def find_yaml_templates(start_dir="/") -> List[str]:
        matches = []
        for root, dirs, files in walk(start_dir):
            if "assets/event_templates" in root:
                for file in files:
                    if file.endswith(".yaml"):
                        matches.append(path.join(root, file))
        return matches

    def __init__(self):
        for yaml_template in self.find_yaml_templates():
            with open(yaml_template) as file:
                template = EventTemplate(yaml.safe_load(file.read()))
                self._list.append(template)

    def get(self, event_type: str) -> EventTemplate:
        return next((template for template in self._list if template.type() == event_type), None)

    def get_events_for_category(self, category: EventCategory) -> List[EventTemplate]:
        return [template for template in self._list if template.category() == category]