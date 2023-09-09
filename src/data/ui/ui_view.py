from typing import List

import bot
from data.ui.buttons import ButtonType, PartyLeaderButton, RoleSelectionButton
from data.db.buttons import ButtonData
from data.ui.views import PersistentView


class UIView:
    """Loading and deleting Buttons from DB."""
    view_list: List[PersistentView] = []

    def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.view_list.clear()
            button_list: List[ButtonData] = []
            for record in db.query('select button_id, label from buttons'):
                button_list.append(ButtonData(record[0], record[1]))
            i = 0
            view = PersistentView()
            self.view_list.append(view)
            for buttondata in button_list:
                i += 1
                if i % 20 == 0:
                    view = PersistentView()
                    self.view_list.append(view)
                if ButtonType.ROLE_SELECTION.value in buttondata.button_id:
                    view.add_item(RoleSelectionButton(label=buttondata.label, custom_id=buttondata.button_id))
                elif ButtonType.PL_POST.value in buttondata.button_id:
                    view.add_item(PartyLeaderButton(label=buttondata.label, custom_id=buttondata.button_id))
            for view in self.view_list:
                bot.instance.add_view(view)
        finally:
            db.disconnect()

    def delete(self, message_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from buttons where button_id ~ \'{message_id}\'')
        finally:
            db.disconnect()