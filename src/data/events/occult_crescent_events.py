from datetime import timedelta
from typing import Tuple
from data.events.event import Event, EventCategory

class OccultCrescent(Event):
    @classmethod
    def category(cl) -> EventCategory: return EventCategory.OC
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
            f'4: {pl4}\n'
            f'5: {pl5}\n'
            f'6: {pl6}\n'
            'Please note, your assignment may be removed at the Raid Leader\'s discretion.'
        )
    @classmethod
    def party_leader_dm_text(cl, party: str, passcode: int) -> str:
        return (
            f'You\'re leading **party {party}.**\n'
            f'The passcode is {str(passcode)}.'
        )
    @classmethod
    def raid_leader_dm_text(cl, passcode_main: int, passcode_supp: int, use_support: bool) -> str:
        return (
            f'Passcode for all parties will be: **{str(passcode_main).zfill(4)}**\n'
            'These passcode(s) have been sent to the relevant party leaders.\n'
            'The passcode(s) will be posted automatically at the appropriate time for that run.'
        )
    @classmethod
    def pl_passcode_delay(cl) -> timedelta: return timedelta(minutes=20)
    @classmethod
    def main_passcode_delay(cl) -> timedelta: return timedelta(minutes=5)
    @classmethod
    def pl_button_texts(cl) -> Tuple[str, str, str, str, str, str, str]:
        return '1', '2', '3', '4', '5', '6', ''
    @classmethod
    def use_support(cl) -> bool: return False

class ForkedTower(OccultCrescent):
    @classmethod
    def type(cl) -> str: return 'FT'
    @classmethod
    def description(cl) -> str: return 'Forked Tower Open Run'
    @classmethod
    def short_description(cl) -> str: return 'FT Open Run'