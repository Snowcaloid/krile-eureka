from typing import List

import bot
from data.ui.buttons import delete_buttons, load_button
from data.ui.views import PersistentView


class UIView:
    """Loading and deleting Buttons from DB."""
    view_list: List[PersistentView] = []

    async def load(self) -> None:
        db = bot.instance.data.db
        db.connect()
        try:
            self.view_list.clear()
            last_message = 0
            for record in db.query('select button_id, message_id from buttons'):
                if last_message != record[1]:
                    view = PersistentView()
                    self.view_list.append(view)
                    last_message = record[1]
                button = await load_button(record[0])
                view.add_item(button)
            for view in self.view_list:
                bot.instance.add_view(view)
        finally:
            db.disconnect()

    def delete(self, message_id: int) -> None:
        delete_buttons(message_id)