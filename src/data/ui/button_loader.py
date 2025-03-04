
from centralized_data import Bindable

from data.db.sql import SQL
from data.ui.base_button import delete_buttons, load_button
from data.ui.views import PersistentView

class ButtonLoader(Bindable):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    """Loading and deleting Buttons from DB."""
    async def load(self) -> None:
        for message_record in SQL('buttons').select(fields=['message_id'],
                                                    group_by=['message_id'],
                                                    all=True):
            view = PersistentView()
            for record in SQL('buttons').select(fields=['button_id'],
                                                where=f"message_id = '{message_record["message_id"]}'",
                                                all=True):
                button = await load_button(record['button_id'])
                view.add_item(button)
            self.bot.client.add_view(view)

    def delete(self, message_id: int) -> None:
        delete_buttons(message_id)