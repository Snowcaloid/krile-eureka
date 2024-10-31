
from typing import List
from data.db.sql import SQL, Record
from data.events.signup import SignupTemplate


class GuildSignupTemplates:
    _list: List[SignupTemplate]

    guild_id: int

    def __init__(self):
        self._list = []

    def load(self, guild_id: int) -> None:
        self.guild_id = guild_id
        self._list.clear()
        for record in SQL('signup_templates').select(fields=['id'],
                                           where=f'guild_id={guild_id}',
                                           all=True):
            signup_template = SignupTemplate()
            signup_template.load(record['id'])
            self._list.append(signup_template)

    def get(self, signup_id: int) -> SignupTemplate:
        return next((event for event in self._list if event.id == signup_id), None)

    def add(self, owner: int) -> SignupTemplate:
        id = SQL('signup_templates').insert(Record(guild_id=self.guild_id,
                                                   owner=owner),
                                            returning_field='id')
        self.load(self.guild_id)
        return self.get(id)

    def remove(self, signup_id: int) -> None:
        SQL('signup_templates').delete(f'id={signup_id}')
        SQL('signup_template_slots').delete(f'template_id={signup_id}')
        self.load(self.guild_id)

    def contains(self, event_id: int) -> bool:
        return not self.get(event_id) is None

    @property
    def all(self) -> List[SignupTemplate]:
        return self._list