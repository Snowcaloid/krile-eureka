from centralized_data import Bindable

from data_providers.context import basic_context
from data_writers.buttons import ButtonsWriter
from models.button import ButtonStruct
from models.button.discord_button import DiscordButton
from data_providers.buttons import ButtonsProvider
from ui.views import PersistentView
from utils.logger import FileLogger

class ButtonLoader(Bindable):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    """Loading and deleting Buttons from DB."""
    def load(self) -> None:
        button_structs = ButtonsProvider().find_all()

        # sort by message_id
        button_structs.sort(key=lambda x: x.message_id)

        # create a view for each message_id
        views = {}
        for button_struct in button_structs:
            if button_struct.message_id not in views:
                views[button_struct.message_id] = PersistentView()
            discord_button = DiscordButton(button_struct)
            views[button_struct.message_id].add_item(discord_button)

        for message_id, view in views.items():
            view.message_id = message_id
            self.bot._client.add_view(view)

    def delete(self, message_id: int) -> None:
        ButtonsWriter().remove(
            ButtonStruct(message_id=message_id),
            basic_context(0, 0, FileLogger())
        )