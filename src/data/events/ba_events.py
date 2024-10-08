from datetime import timedelta
from typing import Tuple
from data.events.event import Event, EventCategory

class BA_Normal(Event):
    @classmethod
    def type(cl) -> str: return 'BA'
    @classmethod
    def description(cl) -> str: return 'Baldesion Arsenal Open Run'
    @classmethod
    def short_description(cl) -> str: return 'BA Open Run'
    @classmethod
    def category(cl) -> EventCategory: return EventCategory.BA
    @classmethod
    def use_passcodes(cl) -> bool: return True
    @classmethod
    def use_pl_posts(cl) -> bool: return True
    @classmethod
    def main_passcode_text(cl, rl: str, passcode: int) -> str:
        return (
            f'Raid Leader: {rl}.\n\n'
            f'**The passcode for all Parties 1-6 is {str(passcode).zfill(4)}.**\n'
            'This will not work for the Support Party.\n\n'
            'Notes:\n'
            '1: Please bring proper logograms. If you do not bring and use Spirit of the Remembered we will not revive you.\n'
            '2: We can not revive players normally in BA, so please bear this in mind and do mechanics properly.\n'
            '3: If you die on trash mobs, this will usually result in you not being revived. There is no reason to die on them, so please wait 5s for the tank to establish aggro.'
        )
    @classmethod
    def support_passcode_text(cl, rl: str, passcode: int) -> str:
        return (
            f'Raid Leader: {rl}.\n\n'
            f'**The Support Party passcode is {str(passcode).zfill(4)}.**\n\n'
            'Notes:\n'
            '1: Please bring proper logograms. If you do not bring and use Spirit of the Remembered we will not revive you.\n'
            '2: We can not revive players normally in BA, so please bear this in mind and do mechanics properly.\n'
            '3: If you die on trash mobs, this will usually result in you not being revived. There is no reason to die on them, so please wait 5s for the tank to establish aggro.'
        )
    @classmethod
    def pl_post_text(cl, rl: str, pl1: str, pl2: str, pl3: str,
                     pl4: str, pl5: str, pl6: str, pls: str) -> str:
        support = f'Support: {pls}\n\n' if pls else 'Support party has been excluded manually by the raid leader.\n\n'
        return (
            f'Raid Leader: {rl}\n'
            f'1: {pl1}\n'
            f'2: {pl2}\n'
            f'3: {pl3}\n'
            f'4: {pl4}\n'
            f'5: {pl5}\n'
            f'6: {pl6}\n'
            f'{support}'
            'Please note, your assignment may be removed at the Raid Leader\'s discretion.'
        )
    @classmethod
    def party_leader_dm_text(cl, party: str, passcode: int) -> str:
        return (
            f'You\'re leading party {party}.\n'
            f'[SoB] BA run party {party}\n'
            f'Passcode is **{str(passcode).zfill(4)}**.'
        )
    @classmethod
    def support_party_leader_dm_text(cl, passcode: int) -> str:
        return (
            'You\'re leading **the support party.**\n'
            f'[SoB] BA support party\n'
            f'Passcode is {str(passcode).zfill(4)}.'
        )
    @classmethod
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int, use_support: bool) -> str:
        if use_support:
            support = f'Passcode for the Support Party will be: **{str(passcode_supp).zfill(4)}**\n'
        else:
            support = f'Support party has been excluded manually by the raid leader. The support passcode will not be posted. In case this is changed, the passcode is **{str(passcode_supp).zfill(4)}**.\n'
        return (
            f'Passcode for the Alliance will be: **{str(passcode_main).zfill(4)}**\n{support}'
            'These passcode(s) have been sent to the relevant party leaders.\n'
            'The passcode(s) will be posted automatically at the appropriate time for that run.'
        )
    @classmethod
    def pl_passcode_delay(cl) -> timedelta: return timedelta(minutes=30)
    @classmethod
    def support_passcode_delay(cl) -> timedelta: return timedelta(minutes=20)
    @classmethod
    def main_passcode_delay(cl) -> timedelta: return timedelta(minutes=15)
    @classmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]:
        return '1', '2', '3', '4', '5', '6', 'Support'
    @classmethod
    def use_support(cl) -> bool: return True

class BA_Reclear(BA_Normal):
    @classmethod
    def type(cl) -> str: return 'BARC'
    @classmethod
    def description(cl) -> str: return 'Baldesion Arsenal Reclear Run'
    @classmethod
    def short_description(cl) -> str: return 'BA Reclear Run'

class BA_Collab(BA_Normal):
    @classmethod
    def type(cl) -> str: return 'BACOLLAB'
    @classmethod
    def description(cl) -> str: return 'Baldesion Arsenal Collaboration Run'
    @classmethod
    def short_description(cl) -> str: return 'BA Collab Run'
    @classmethod
    def use_passcodes(cl) -> bool: return False
    @classmethod
    def use_pl_posts(cl) -> bool: return False

class BA_Special(BA_Normal):
    @classmethod
    def type(cl) -> str: return 'BASPEC'
    @classmethod
    def description(cl) -> str: return 'Baldesion Arsenal Special Run'
    @classmethod
    def short_description(cl) -> str: return 'BA Special Run'

class BA_16Man_Provisionary(BA_Normal):
    @classmethod
    def type(cl) -> str: return 'BA16_PROV'
    @classmethod
    def description(cl) -> str: return 'Baldesion Arsenal 16 Man Run'
    @classmethod
    def short_description(cl) -> str: return 'BA 16 Man'
    @classmethod
    def pl_post_text(cl, rl: str, pl1: str, pl2: str, pl3: str,
                     pl4: str, pl5: str, pl6: str, pls: str) -> str:
        return (
            f'Raid Leader: {rl}\n'
            f'1: {pl1}\n'
            f'2: {pl2}\n'
            'Please note, your assignment may be removed at the Raid Leader\'s discretion.'
        )
    @classmethod
    def use_support(cl) -> bool: return False
    @classmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]:
        return '1', '2', '', '', '', '', ''
    @classmethod
    def main_passcode_delay(cl) -> timedelta: return timedelta(minutes=30)