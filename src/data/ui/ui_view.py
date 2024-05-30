from typing import List

import bot
from data.ui.buttons import load_button
from data.ui.views import PersistentView


class UIView:
    """Loading and deleting Buttons from DB."""
    view_list: List[PersistentView] = []

    async def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.view_list.clear()
            i = 0
            for record in db.query('select button_id from buttons'):
                i += 1
                if i == 1 or i % 20 == 0:
                    view = PersistentView()
                    self.view_list.append(view)
                button = await load_button(record[0])
                view.add_item(button)
            for view in self.view_list:
                bot.instance.add_view(view)
        finally:
            db.disconnect()

    def delete(self, message_id: int) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            db.query(f'delete from buttons where message_id = {str(message_id)}')
        finally:
            db.disconnect()