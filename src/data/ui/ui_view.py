from typing import List

import bot
from data.db.sql import SQL
from data.ui.buttons import delete_buttons, load_button
from data.ui.views import PersistentView


class UIView:
    """Loading and deleting Buttons from DB."""
    view_list: List[PersistentView] = []

    async def load(self) -> None:
        self.view_list.clear()
        last_message = 0
        for record in SQL('buttons').select(fields=['button_id', 'message_id'], all=True):
            if last_message != record['message_id']:
                view = PersistentView()
                self.view_list.append(view)
                last_message = record['message_id']
            button = await load_button(record['button_id'])
            view.add_item(button)
        for view in self.view_list:
            bot.instance.add_view(view)

    def delete(self, message_id: int) -> None:
        delete_buttons(message_id)