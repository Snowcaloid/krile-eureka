
from datetime import timedelta
from typing import Tuple
from data.events.event import Event, EventCategory

class SignupEvent(Event):
    @classmethod
    def type(cl) -> str: return 'Signup'
    @classmethod
    def description(cl) -> str: return 'Custom Signup Run'
    @classmethod
    def short_description(cl) -> str: return 'Custom Signup Run'
    @classmethod
    def category(cl) -> EventCategory: return EventCategory.CUSTOM
    @classmethod
    def use_passcodes(cl) -> bool: return True
    @classmethod
    def use_pl_posts(cl) -> bool: return True # use for recruitment posts
    @classmethod
    def party_leader_dm_text(cl, party: str, passcode: int) -> str:
        return (
            f'You\'re leading party {party}.\n'
            f'[SoB] Custom Signup Run party {party}\n'
            f'Passcode is **{str(passcode).zfill(4)}**.'
        )
    @classmethod
    def support_party_leader_dm_text(cl, passcode: int) -> str:
        return (
            'You\'re leading **the support party.**\n'
            f'[SoB] Custom Signup Run support party\n'
            f'Passcode is {str(passcode).zfill(4)}.'
        )
    @classmethod
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int, use_support: bool) -> str:
        if not cl.use_support:
            support = ''
        elif use_support:
            support = f'Passcode for the Support Party will be: **{str(passcode_supp).zfill(4)}**\n'
        else:
            support = f'Support party has been excluded manually by the raid leader. The support passcode will not be posted. In case this is changed, the passcode is **{str(passcode_supp).zfill(4)}**.\n'
        return (
            f'Passcode for the Alliance will be: **{str(passcode_main).zfill(4)}**\n{support}'
            'These passcode(s) have been sent to the relevant party leaders and members.\n'
        )#
    @classmethod
    def pl_passcode_delay(cl) -> timedelta: return timedelta(minutes=15)
    @classmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]:
        return '1', '2', '3', '4', '5', '6', 'Support'
    @classmethod
    def use_support(cl) -> bool: return True