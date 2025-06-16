from centralized_data import Bindable

from data.db.sql import _SQL, ReadOnlyConnection
from models.button import ButtonStruct
from models.button.discord_button import DiscordButton
from data_providers.buttons import ButtonsProvider
from ui.base_button import delete_buttons
from ui.views import PersistentView

class ButtonLoader(Bindable):
    from bot import Bot
    @Bot.bind
    def bot(self) -> Bot: ...

    """Loading and deleting Buttons from DB."""
    def load(self) -> None:
        with ReadOnlyConnection() as connection: #TODO: move this into the provider or somewhere else to avoid double db access
            for message_record in connection.sql('buttons').select(fields=['message_id'],
                                                        group_by=['message_id'],
                                                        all=True):
                view = PersistentView()
                for record in connection.sql('buttons').select(fields=['button_id'],
                                                    where=f"message_id = '{message_record["message_id"]}'",
                                                    all=True):
                    discord_button = DiscordButton(ButtonsProvider().find(
                        ButtonStruct(button_id=record['button_id'])))
                    view.add_item(discord_button)
                self.bot._client.add_view(view)

    def delete(self, message_id: int) -> None:
        delete_buttons(message_id)