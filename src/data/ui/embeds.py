import bot
from typing import List

from discord import Embed, Message
from discord.ui import Button
from data.ui.buttons import ButtonType, MissedRunButton, PartyLeaderButton, RoleSelectionButton, button_custom_id

from data.ui.views import PersistentView

class EmbedButtonData:
    id: str
    label: str
    def __init__(self, label: str):
        self.id = ''
        self.label = label

class EmbedEntry:
    """Helper class for embed entries."""
    _id_counter: int

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
        self._id_counter = 0
        self.image = ''
        self.thumbnail = ''
        self.buttons = []

    def add_desc_line(self, desc: str):
        self.desc_lines.append(desc)

    def edit_desc_line(self, line: int, desc: str):
        self.desc_lines[line] = desc

    def remove_desc_line(self, line: int):
        if line < len(self.desc_lines):
            self.desc_lines.remove(self.desc_lines[line])

    def add_field(self, field: object):
        field["id"] = self._id_counter
        self._id_counter += 1
        self.fields.append(field)

    def edit_field(self, id: int, field: object):
        for fld in self.fields:
            if fld["id"] == id:
                self.fields[self.fields.index(fld)] = field

    def remove_field(self, id: int):
        for field in self.fields:
            if field["id"] == id:
                self.fields.remove(field)
                break

    def add_button(self, label: str):
        self.buttons.append(EmbedButtonData(label))

    def edit_button(self, oldlabel: str, newlabel: str):
        for button in self.buttons:
            if button.label.lower() == oldlabel.lower():
                button.label = newlabel

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

    def create_view(self, debug: bool, message: Message = None, button_type: ButtonType = ButtonType.ROLE_SELECTION) -> PersistentView:
        if not self.buttons: return None
        view = PersistentView()
        for button in self.buttons:
            if debug:
                view.add_item(Button(label=button.label, disabled=True))
            elif message:
                button.id = button_custom_id(button.label, message, button_type)
                if button_type == ButtonType.ROLE_SELECTION:
                    view.add_item(RoleSelectionButton(label=button.label, custom_id=button.id))
                elif button_type == ButtonType.MISSEDRUN:
                    view.add_item(MissedRunButton(label=button.label, custom_id=button.id))
                elif button_type == ButtonType.PL_POST:
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

    def load_from_embed(self, user: int, message: Message):
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
                    entry.add_button(button.label)

    def save(self, user: int):
        """Saves the created buttons to the database.
        Args:
            user (int): querying user id
        """
        if self.get(user).buttons:
            bot.instance.data.db.connect()
            try:
                for button in self.get(user).buttons:
                    if not bot.instance.data.db.query(f'select button_id from buttons where button_id=\'{button.id}\''):
                        bot.instance.data.db.query(f'insert into buttons values (\'{button.id}\', \'{button.label}\')')
            finally:
                bot.instance.data.db.disconnect()