from datetime import datetime, timedelta
from typing import Tuple
from data.events.event import Event, EventCategory

class DRS_Normal(Event):
    @classmethod
    def type(cl) -> str: return 'DRS'
    @classmethod
    def description(cl) -> str: return 'DRS Prog Run'
    @classmethod
    def short_description(cl) -> str: return 'DRS Prog Run'
    @classmethod
    def category(cl) -> EventCategory: return EventCategory.DRS
    @classmethod
    def use_passcodes(cl) -> bool: return True
    @classmethod
    def use_pl_posts(cl) -> bool: return True
    @classmethod
    def use_pl_post_thread(cl) -> bool: return True
    @classmethod
    def pl_post_thread_title(cl, time: datetime) -> str:
        return f'{time.strftime("%A, %d %B %Y")} {cl.description()}'
    @classmethod
    def delete_pl_posts(cl) -> bool: return False
    @classmethod
    def use_support(cl) -> bool: return False
    @classmethod
    def main_passcode_text(cl, rl: str, passcode: int) -> str:
        return (
            f'Raid Leader: {rl}.\n\n'
            f'**The passcode for all parties is {str(passcode)}.**\n\n'
            'Notes:\n'
            '1: Please bring actions and pure essences as shown in our DRS Action Guide (This may differ to what you hold if you have progged on another server),\n'
            '2: Prioritise mechanics over damage,\n'
            '3: Listen to Raid Leaders and Party Leaders,\n'
            '4: Most Importantly: Relax and don\'t stress.'
        )
    @classmethod
    def pl_post_text(cl, rl: str, pl1: str, pl2: str, pl3: str,
                     pl4: str, pl5: str, pl6: str, pls: str) -> str:
        return (
            f'Raid Leader: {rl}\n'
            f'A: {pl1}\n'
            f'B: {pl2}\n'
            f'C: {pl3}\n'
            f'D: {pl4}\n'
            f'E: {pl5}\n'
            f'F: {pl6}\n'
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
        return 'A', 'B', 'C', 'D', 'E', 'F', ''

class DRS_Reclear(DRS_Normal):
    @classmethod
    def type(cl) -> str: return 'DRSRC'
    @classmethod
    def description(cl) -> str: return 'DRS Reclear Run'
    @classmethod
    def short_description(cl) -> str: return 'DRS Reclear Run'