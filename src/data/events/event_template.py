
from datetime import datetime, timedelta
from json import dumps
from typing import Dict, Tuple
from asset_loader import YamlAsset
from data.events.event_category import EventCategory
from discord.app_commands import Choice

from utils import get_discord_timestamp


class EventTemplate(YamlAsset):
    def autocomplete_weight(self) -> int:
        category_weight = {
            EventCategory.CUSTOM: 0,
            EventCategory.BA: 1,
            EventCategory.CHAOTIC: 2,
            EventCategory.DRS: 3,
            EventCategory.BOZJA: 4
        }
        return category_weight[self.category()] * 100 + 10 - len(self.type()) # the longer the type, the less specific it is

    @property
    def data(self) -> str:
        return dumps(self.source)

    def _handle_support_text(self, use_support: bool, template_text: str) -> str:
        index_of_no_support = template_text.find('%!support=') if '%!support=' in template_text else -1
        no_support_text = template_text[index_of_no_support + len('%!support='):] if '%!support=' in template_text else ''
        if index_of_no_support == -1:
            support_text = template_text[template_text.find('%support=') + len('%support='):] if '%support=' in template_text else ''
        else:
            support_text = template_text[template_text.find('%support=') + len('%support='):template_text.find('%!support=')] if '%support=' in template_text else ''

        if '%support=' in template_text:
            template_text = template_text[:template_text.find('%support=')]
        elif '%!support=' in template_text:
            template_text = template_text[:template_text.find('%!support=')]

        if self.use_support() and use_support:
            return template_text.replace('%support', support_text)
        else:
            return template_text.replace('%support', no_support_text)

    def type(self) -> str:
        return self.source.get('type', 'CUSTOM')

    def description(self) -> str:
        return self.source.get('description', 'Custom run')

    def short_description(self) -> str:
        return self.source.get('short_description', 'Custom run')

    def category(self) -> EventCategory:
        return EventCategory(self.source.get('category', 'CUSTOM'))

    def use_recruitment_posts(self) -> bool:
        return self.source.get('use_recruitment_posts', False)

    def use_passcodes(self) -> bool:
        return self.source.get('use_passcodes', False)

    def recruitment_post_title(self, time: datetime) -> str:
        value = self.source.get('recruitment_post_title', (
            '%time ST (%localtime LT): %description Party Leader Recruitment'
        ))
        return value.replace('%time', time.strftime(f"%A, %d-%b-%y %H:%M ST")).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', self.description())

    def recruitment_post_text(self,
                              rl: str, pl1: str, pl2: str, pl3: str,
                              pl4: str, pl5: str, pl6: str, pls: str,
                              use_support: bool) -> str:
        value = self.source.get('recruitment_post_text', (
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
        list = self.source.get('pl_button_texts', ['1', '2', '3', '4', '5', '6', 'Support'])
        if len(list) < 7: list = list + [''] * (7 - len(list)) # Fill up with empty strings
        return tuple(list)

    def use_recruitment_post_threads(self) -> bool:
        return self.source.get('use_recruitment_post_threads', False)

    def delete_recruitment_posts(self) -> bool:
        return self.source.get('delete_recruitment_posts', True)

    def recruitment_post_thread_title(self, time: datetime) -> str:
        value = self.source.get('recruitment_post_thread_title', f'%time {self.description()}')
        return value.replace('%time', time.strftime('%A, %d %B %Y'))

    def use_support(self) -> bool:
        return self.source.get('use_support', False)

    def main_passcode_text(self, rl: str, passcode: int) -> str:
        value = self.source.get('main_passcode_text',(
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
        value = self.source.get('support_passcode_text', (
            f'Raid Leader: %rl.\n\n'
            f'**The Support Party passcode is **%passcode.**\n\n'
            'Notes:\n'
            '1: Please bring proper logograms. If you do not bring and use Spirit of the Remembered we will not revive you.\n'
            '2: We can not revive players normally in BA, so please bear this in mind and do mechanics properly.\n'
            '3: If you die on trash mobs, this will usually result in you not being revived. There is no reason to die on them, so please wait 5s for the tank to establish aggro.'
        ))
        return value.replace('%rl', rl).replace('%passcode', str(passcode).zfill(4))

    def dm_title(self, time: datetime) -> str:
        value = self.source.get('dm_title', (
            '%time ST (%localtime LT) %description Passcode Notification'
        ))
        return value.replace('%time', time.strftime(f"%A, %d-%b-%y %H:%M ST")).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', self.description())

    def party_leader_dm_text(self, party: str, passcode: int) -> str:
        value = self.source.get('party_leader_dm_text', (
            f'You\'re leading **party %party.**\n'
            f'Passcode is **%passcode**.'
        ))
        return value.replace('%party', party).replace('%passcode', str(passcode).zfill(4))

    def support_party_leader_dm_text(self, passcode: int) -> str:
        value = self.source.get('support_party_leader_dm_text', (
            'You\'re leading **the support party.**\n'
            f'Passcode is **%passcode**.'
        ))
        return value.replace('%passcode', str(passcode).zfill(4))

    def raid_leader_dm_text(self, passcode_main: int, passcode_supp: int, use_support: bool) -> str:
        value = self.source.get('raid_leader_dm_text', (
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
        return timedelta(minutes=self.source.get('pl_passcode_delay', 30))

    def support_passcode_delay(self) -> timedelta:
      return timedelta(minutes=self.source.get('support_passcode_delay', 20))

    def main_passcode_delay(self) -> timedelta:
        return timedelta(minutes=self.source.get('main_passcode_delay', 15))

    def schedule_entry_text(self, rl: str, time: datetime, custom: str, use_support: bool) -> str:
        value = self.source.get('schedule_entry_text', (
            '(%time ST (%localtime LT)): %description (%rl)%support%!support= __(No support)__'
        ))
        value = self._handle_support_text(use_support, value)
        return value.replace('%time', time.strftime('%H:%M')).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', custom).replace('%rl', rl)

    def passcode_post_title(self, time: datetime) -> str:
        value = self.source.get('passcode_post_title', (
            '%time ST (%localtime LT): %description Passcode'
        ))
        return value.replace('%time', time.strftime(f"%A, %d-%b-%y %H:%M ST")).replace('%localtime', get_discord_timestamp(time)).replace(
            '%description', self.description())

    def is_signup(self) -> bool:
        return self.source.get('is_signup', False)

    def as_choice(self) -> Choice:
        return Choice(name=self.description(), value=self.type())

class CustomEventTamplate(EventTemplate):
    def __init__(self, guild_id: int, source: Dict):
        self.guild_id = guild_id
        self.source = source