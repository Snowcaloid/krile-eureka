import bot as ded_bot
from typing import List

from discord import Embed, Message
from discord.ui import Button
from buttons import ButtonType, RoleSelectionButton
from utils import button_custom_id

from views import PersistentView

class ButtonData:
    id: str
    label: str
    def __init__(self, label: str):
        self.id = ''
        self.label = label
        
class EmbedEntry:
    """Helper class for embed entries."""
    _id_counter: int
    
    user: int
    title: str
    desc_lines: List[str]
    fields: List[object]
    image: str
    thumbnail: str
    buttons: List[ButtonData]
    
    def __init__(self, user: int):
        self.user = user
        self.title = 'Use /embed title to change the title'
        self.desc_lines = []
        self.fields = []
        self._id_counter = 0
        self.image = ''
        self.thumbnail = ''
        self.buttons = []

    def add_desc_line(self, desc: str):
        """Adds a description for the embed

        Args:
            desc (str): Description to be added
        """
        self.desc_lines.append(desc)
        
    def edit_desc_line(self, line: int, desc: str):
        """Edits a description for the embed

        Args:
            line (int): line # to be changed
            desc (str): Description to be set
        """
        self.desc_lines[line] = desc
        
    def remove_desc_line(self, line: int):
        """Removes a description line from the embed

        Args:
            line (int): line # to be removed
        """
        if line < len(self.desc_lines):
            self.desc_lines.remove(self.desc_lines[line])

    def add_field(self, field: object):
        """Adds a field for the embed

        Args:
            field (object): object {"title", "desc"}
        """
        field["id"] = self._id_counter
        self._id_counter += 1
        self.fields.append(field)

    def edit_field(self, id: int, field: object):
        """Edits a field for the embed

        Args:
            id (int): id of the field to be edited
            field (object): object {"title", "desc"}
        """
        for fld in self.fields:
            if fld["id"] == id:
                self.fields[self.fields.index(fld)] = field

    def remove_field(self, id: int):
        """Adds a field for the embed

        Args:
            id (int): id of the field to be removed
        """
        for field in self.fields:
            if field["id"] == id:
                self.fields.remove(field)
                break
            
    def add_button(self, label: str):
        """Adds a button for the embed

        Args:
            label (str): Role label
        """
        self.buttons.append(ButtonData(label))

    def edit_button(self, oldlabel: str, newlabel: str):
        """Edits a button for the embed

        Args:
            oldlabel (str): old label
            newlabel (str): new label
        """
        for button in self.buttons:
            if button.label.lower() == oldlabel.lower():
                button.label = newlabel
        
        
    def remove_button(self, label: str):
        """Removes a button from the embed

        Args:
            label (str): Role label
        """
        for button in self.buttons:
            if button.label.lower() == label.lower():
                self.buttons.remove(button)

class EmbedData: 
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

    def get_entry(self, user: int) -> EmbedEntry:
        for post in self._list:
            if post.user == user:
                return post
        post = EmbedEntry(user)
        self._list.append(post)
        return post

    def add_desc_line(self, user: int, description: str):
        """Adds a description for the embed

        Args:
            user (int): querying user id
            desc (str): Description to be added
        """
        self.get_entry(user).add_desc_line(description)

    def edit_desc_line(self, user: int, line: int, description: str):
        """Edits a description for the embed

        Args:
            user (int): querying user id
            line (int): line # to be edited
            desc (str): Description to be added
        """
        self.get_entry(user).edit_desc_line(line, description)

    def remove_desc_line(self, user: int, line: int):
        """Adds a description for the embed

        Args:
            user (int): querying user id
            line (int): line # to be removed
        """
        self.get_entry(user).remove_desc_line(line)
        
    def field_exists(self, user: int, id: int) -> bool:
        for field in self.get_entry(user).fields:
            if field["id"] == id:
                return True
        return False

    def add_field(self, user: int, field: object):
        """Adds a description for the embed

        Args:
            user (int): querying user id
            field (object): object {"title", "desc"}
        """
        self.get_entry(user).add_field(field)
        
    def edit_field(self, user: int, id: int, field: object):
        """Edits a description for the embed

        Args:
            user (int): querying user id
            id (int): id of the field to be edited.
            field (object): object {"title", "desc"}
        """
        self.get_entry(user).edit_field(id, field)

    def remove_field(self, user: int, id: int):
        """Adds a description for the embed

        Args:
            user (int): querying user id
            id (int): id of the field to be removed.
        """
        self.get_entry(user).remove_field(id)

    def button_exists(self, user: int, role: str) -> bool:
        for button in self.get_entry(user).buttons:
            if button.label.lower() == role.lower():
                return True
        return False

    def add_button(self, user: int, label: str):
        """Adds a button for the embed

        Args:
            user (int): querying user id
            label (str): Role label
        """
        self.get_entry(user).add_button(label)

    def edit_button(self, user: int, oldlabel: str, newlabel: str):
        """Edits a button for the embed

        Args:
            user (int): querying user id
            oldlabel (str): old label
            newlabel (str): new label
        """
        self.get_entry(user).edit_button(oldlabel, newlabel)

    def remove_button(self, user: int, label: str):
        """Removes a button for the embed

        Args:
            user (int): querying user id
            label (str): label to be removed
        """
        self.get_entry(user).remove_button(label)
        
    def commands(self) -> str:
        return ('title, image, thumbnail, '
                'add_field, edit_field, remove_field, '
                'add_desc, edit_desc, remove_desc')
    
    def finish_command(self) -> str:
        return 'finish'
        
    def create_embed(self, user: int, debug: bool) -> Embed:
        entry = self.get_entry(user)
        desc = ''
        if debug:
            for line in entry.desc_lines:
                desc += f'{line} [#{entry.desc_lines.index(line)}]\n'    
            desc = "\n\n".join([desc, (
                '**Please note that the [#numbers] are only there during the creation and can be used for removal of elements.**\n'
                f'Use {self.commands()} to continue creation or {self.finish_command()} to finish creation.'
                )])
        elif entry.desc_lines:
            desc = "\n".join(entry.desc_lines) 
        embed = Embed(
            title=entry.title,
            description=desc
        )
        for field in entry.fields:
            title = field["title"]
            if debug:
                title += f'[#{field["id"]}]'
            embed.add_field(name=title, value=field["desc"])
        if entry.image:
            embed.set_image(url=entry.image)
        if entry.thumbnail:
            embed.set_thumbnail(url=entry.thumbnail)
        return embed
    
    def create_view(self, user: int, debug: bool, message: Message = None) -> PersistentView:
        """Creates a view for the role post containing buttons

        Args:
            user (int): querying user id
            debug (bool): If true, buttons have no function. Use with 
            False only once per query. 
        """
        view = PersistentView()
        for button in self.get_entry(user).buttons:
            if debug:
                view.add_item(Button(label=button.label, disabled=True))
            elif message:
                button.id = button_custom_id(button.label, message, ButtonType.ROLE_SELECTION)
                view.add_item(RoleSelectionButton(label=button.label, custom_id=button.id))
        return view

    def clear(self, user: int):
        """Removes all entries requested by the user

        Args:
            user (int): querying user id
        """
        for entry in self._list:
            if entry.user == user:
                self._list.remove(entry)
                
    def save(self, user: int):
        """Saves the created Role buttons to the database.

        Args:
            user (int): querying user id
        """
        if self.get_entry(user).buttons:
            ded_bot.snowcaloid.data.db.connect()
            try:
                for button in self.get_entry(user).buttons:
                    ded_bot.snowcaloid.data.db.query(f'insert into buttons values (\'{button.id}\', \'{button.label}\')')
            finally:
                ded_bot.snowcaloid.data.db.disconnect()