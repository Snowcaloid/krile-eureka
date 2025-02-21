
from typing import Dict

from bindable import Bindable
from discord import Message


class MessageCopyController(Bindable):
    _list: Dict[int, Message]

    def __init__(self):
        self._list = {}

    def get(self, user: int) -> Message:
        if user in self._list:
            return self._list[user]
        else:
            return None

    def clear(self, user: int) -> None:
        """Removes the entry requested by the user
            user (int): querying user id
        """
        self._list.pop(user)

    def add(self, user: int, message: Message) -> None:
        self._list[user] = message
