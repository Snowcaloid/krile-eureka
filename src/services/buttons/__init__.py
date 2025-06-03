from typing import override
from models.button import ButtonStruct
from models.context import ServiceContext
from services._base import BaseService

class ButtonsService(BaseService[ButtonStruct]):
    """"manage button"""
    @override
    def sync(self, struct: ButtonStruct, context: ServiceContext) -> None: 
        """Override to sync a struct with the database."""
        with context:
            found_struct = self.provider.find(struct)
            if found_struct:
                edited_struct = found_struct.intersect(struct)
                self.db.update(edited_struct.to_record(), f'id={found_struct.id}')
                context.log(f"[BUTTONS] {edited_struct.label} updated successfully.")
                context.log(f"Changes: ```{edited_struct.changes_since(found_struct)}```")
            elif self._user_input.can_insert(struct):
                self.db.insert(struct.to_record())
                context.log(f"[BUTTONS] {struct.label} added successfully.")
                context.log(f"Button:```{struct}```")
            self.load()

    @override
    def remove(self, struct: ButtonStruct, context: ServiceContext) -> None: ...
    """Override to remove a struct from the database."""