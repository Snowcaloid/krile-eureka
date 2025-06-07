from typing import override
from data.db.sql import SQL
from models.button import ButtonStruct
from models.context import ExecutionContext
from providers.buttons import ButtonsProvider
from services._base import BaseService

class ButtonsService(BaseService[ButtonStruct]):
    """"manage button"""
    @ButtonsProvider.bind
    def _button_provider(self) -> ButtonsProvider: ...
    @override
    def sync(self, struct: ButtonStruct, context: ExecutionContext) -> None:
        """Override to sync a struct with the database."""
        with context:
            found_struct = self._button_provider.find(struct)
            if found_struct:
                edited_struct = found_struct.intersect(struct)
                SQL('buttons').update(
                    edited_struct.to_record(),
                    f'id={found_struct.button_id}')
                context.log(f"[BUTTONS] {edited_struct.label} updated successfully.")
                context.log(f"Changes: ```{edited_struct.changes_since(found_struct)}```")
            else:
                SQL('buttons').insert(struct.to_record())
                context.log(f"[BUTTONS] {struct.label} added successfully.")
                context.log(f"Button:```{struct}```")
            self._button_provider.load()

    @override
    def remove(self, struct: ButtonStruct, context: ExecutionContext) -> None:
        """Override to remove a struct from the database."""
        with context:
            found_struct = self._button_provider.find(struct)
            if found_struct:
                SQL('buttons').delete(f'button_id={found_struct.button_id}')
                context.log(f"[BUTTONS] {found_struct.label} removed successfully.")
            else:
                context.log(f"[BUTTONS] Button {struct.label} not found for removal.")
            self._button_provider.load()