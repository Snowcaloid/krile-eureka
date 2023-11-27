import bot
from typing import List
from re import search

from discord import Embed, Message
from discord.ui import Button
from data.ui.buttons import ButtonType, MissedRunButton, PartyLeaderButton, RoleSelectionButton, button_custom_id

from data.ui.views import PersistentView

class EmbedButtonData:
    id: str
    label: str
    type: ButtonType
    def __init__(self, label: str, button_type: ButtonType):
        self.id = ''
        self.label = label
        self.type = button_type

class EmbedEntry:
    """Helper class for embed entries."""

    user: int
    message: Message
    title: str
    desc_lines: List[str]
    fields: List[object]
    image: str
    thumbnail: str
    buttons: List[EmbedButtonData]

    def __init__(self, user: int):
        self.user = user
        self.message = None
        self.title = 'Use /embed title to change the title'
        self.desc_lines = []
        self.fields = []
        self.image = ''
        self.thumbnail = ''
        self.buttons = []

    def add_desc_line(self, desc: str):
        self.desc_lines.append(desc)

    def edit_desc_line(self, line: int, desc: str):
        self.desc_lines[line] = desc

    def insert_desc_line(self, line: int, desc: str):
        self.desc_lines.insert(line, desc)

    def remove_desc_line(self, line: int):
        if line < len(self.desc_lines):
            self.desc_lines.remove(self.desc_lines[line])

    def add_field(self, field: object):
        self.fields.append(field)
        field["id"] = self.fields.index(field)

    def edit_field(self, id: int, field: object):
        if id < len(self.fields):
            self.fields[id] = field

    def insert_field(self, id: int, field: object):
        if id < len(self.fields):
            self.fields.insert(id, field)
            field["id"] = id
            for fld in self.fields:
                if fld["id"] >= id and fld != field:
                    fld["id"] = fld["id"] + 1

    def remove_field(self, id: int):
        for field in self.fields:
            if field["id"] == id:
                self.fields.remove(field)
                for fld in self.fields:
                    if fld["id"] >= id:
                        fld["id"] = fld["id"] - 1
                break

    def add_button(self, label: str, button_type: ButtonType):
        self.buttons.append(EmbedButtonData(label, button_type))

    def edit_button(self, label: str, newlabel: str, button_type: ButtonType = None):
        for button in self.buttons:
            if button.label.lower() == label.lower():
                if newlabel:
                    button.label = newlabel
                if button_type:
                    button.type = button_type
                break

    def insert_button(self, position: int, label: str, button_type: ButtonType):
        for button in self.buttons:
            if self.buttons.index(button) == position:
                self.buttons.insert(self.buttons.index(button), EmbedButtonData(label, button_type))
                break

    def remove_button(self, label: str):
        for button in self.buttons:
            if button.label.lower() == label.lower():
                self.buttons.remove(button)

    def field_exists(self, id: int) -> bool:
        for field in self.fields:
            if field["id"] == id:
                return True
        return False

    def button_exists(self, label: str) -> bool:
        for button in self.buttons:
            if button.label.lower() == label.lower():
                return True
        return False

    def create_embed(self, debug: bool) -> Embed:
        desc = ''
        if debug:
            for line in self.desc_lines:
                desc += f'{line} [#{self.desc_lines.index(line)}]\n'
            desc = "\n\n".join([desc, (
                '**Please note that the [#numbers] are only there during the creation and can be used for removal of elements.**\n'
                f'Use other embed commands to continue or finish creation.'
                )])
        elif self.desc_lines:
            desc = "\n".join(self.desc_lines)
        embed = Embed(
            title=self.title,
            description=desc
        )
        for field in self.fields:
            title = field["title"]
            if debug:
                title += f'[#{field["id"]}]'
            embed.add_field(name=title, value=field["desc"])
        if self.image:
            embed.set_image(url=self.image)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed

    def create_view(self, debug: bool, message: Message = None) -> PersistentView:
        view = PersistentView()
        for button in self.buttons:
            if debug:
                view.add_item(Button(label=button.label, disabled=True))
            elif message:
                button.id = button_custom_id(button.label, message, button.type)
                if button.type == ButtonType.ROLE_SELECTION:
                    view.add_item(RoleSelectionButton(label=button.label, custom_id=button.id))
                elif button.type == ButtonType.MISSEDRUN:
                    view.add_item(MissedRunButton(label=button.label, custom_id=button.id))
                elif button.type == ButtonType.PL_POST:
                    view.add_item(PartyLeaderButton(label=button.label, custom_id=button.id))
        return view

class EmbedController:
    """Runtime data object containing temporary data for creating an embed post.
    This object has no equivalent database entity.

    Properties
    ----------
    _list: :class:`List[EmbedEntry]`
        List of all embed posts in creation.
    """
    _list: List[EmbedEntry]

    def __init__(self):
        self._list = []

    def get(self, user: int) -> EmbedEntry:
        for post in self._list:
            if post.user == user:
                return post
        post = EmbedEntry(user)
        self._list.append(post)
        return post

    def clear(self, user: int):
        """Removes all entries requested by the user
            user (int): querying user id
        """
        for entry in self._list:
            if entry.user == user:
                self._list.remove(entry)

    def load_from_message(self, user: int, message: Message):
        """Creates runtime embed data with informations from the embed."""
        embed = message.embeds[0]
        self.clear(user)
        entry = self.get(user)
        entry.message = message
        entry.title = embed.title if embed.title else ''
        entry.desc_lines = embed.description.splitlines() if embed.description else []
        entry.image = embed.image if embed.image else ''
        entry.thumbnail = embed.thumbnail if embed.thumbnail else ''
        for field in embed.fields:
            entry.add_field({"title": field.name, "desc": field.value})
        view = PersistentView.from_message(message)
        if view:
            for button in view.children:
                if isinstance(button, Button):
                    type_match = search(r'(@[^@]+@)', button.custom_id)
                    if type_match:
                        button_type = ButtonType(type_match.group(1))
                    else:
                        button_type = ButtonType.ROLE_SELECTION

                    entry.add_button(button.label, button_type)
