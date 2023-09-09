from datetime import timedelta
from typing import Tuple
from event import Event, EventCategory

class BozjaBase(Event):
    @classmethod
    def category(cl) -> EventCategory: return EventCategory.BOZJA
    @classmethod
    def use_pl_posts(cl) -> bool: return True
    @classmethod
    def use_passcodes(cl) -> bool: return True
    @classmethod
    def main_passcode_text(cl, rl: str, passcode: int) -> str:
        return (
            f'Raid Leader: {rl}.\n\n'
            f'**The passcode for all parties is {str(passcode)}.**'
        )
    @classmethod
    def pl_post_text(cl, rl: str, pl1: str, pl2: str, pl3: str,
                     pl4: str, pl5: str, pl6: str, pls: str) -> str:
        return (
            f'Raid Leader: {rl}\n'
            f'1: {pl1}\n'
            f'2: {pl2}\n'
            f'3: {pl3}\n'
            'Please note, your assignment may be removed at the Raid Leader\'s discretion.'
        )
    @classmethod
    def party_leader_dm_text(cl, party: str, passcode: int) -> str:
        return (
            f'You\'re leading **party {party}.**\n'
            f'Passcode is {str(passcode)}.'
        )
    @classmethod
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int) -> str:
        return (
            f'Passcode for all parties will be: {passcode_main}\n'
            'These passcode(s) have been sent to the relevant party leaders.\n'
            'The passcode(s) will be posted automatically at the appropriate time for that run.'
        )
    @classmethod
    def pl_passcode_delay(cl) -> timedelta: return timedelta(minutes=45)
    @classmethod
    def main_passcode_delay(cl) -> timedelta: return timedelta(minutes=15)
    @classmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]:
        return '1', '2', '3', '', '', '', ''
    @classmethod
    def use_support(cl) -> bool: return False

class DRN_Newbie(BozjaBase):
    @classmethod
    def type(cl) -> str: return 'DRN'
    @classmethod
    def description(cl) -> str: return 'Delubrum Reginae Newbie Run'
    @classmethod
    def short_description(cl) -> str: return 'DRN Newbie Run'

class DRN_Reclear(BozjaBase):
    @classmethod
    def type(cl) -> str: return 'DRNRC'
    @classmethod
    def description(cl) -> str: return 'Delubrum Reginae Speedrun'
    @classmethod
    def short_description(cl) -> str: return 'DRN Speedrun'

class Castrum(BozjaBase):
    @classmethod
    def type(cl) -> str: return 'CASTRUM'
    @classmethod
    def description(cl) -> str: return 'Castrum Lacus Litore Run'
    @classmethod
    def short_description(cl) -> str: return 'CLL Run'

class Dalriada(BozjaBase):
    @classmethod
    def type(cl) -> str: return 'DALRIADA'
    @classmethod
    def description(cl) -> str: return 'Dalriada Run'
    @classmethod
    def short_description(cl) -> str: return 'Dalriada Run'

class CastrumAndDalriada(BozjaBase):
    @classmethod
    def type(cl) -> str: return 'CASDAL'
    @classmethod
    def description(cl) -> str: return 'CLL + Dalriada Run'
    @classmethod
    def short_description(cl) -> str: return 'CLL + Dalriada  Run'

class BozjaAllRounder(BozjaBase):
    @classmethod
    def type(cl) -> str: return 'BOZJAALL'
    @classmethod
    def description(cl) -> str: return 'CLL + Dalriada + DRN Run'
    @classmethod
    def short_description(cl) -> str: return 'CLL + Dalriada + DRN Run'

DRN_Newbie.register()
DRN_Reclear.register()
Castrum.register()
Dalriada.register()
CastrumAndDalriada.register()
BozjaAllRounder.register()