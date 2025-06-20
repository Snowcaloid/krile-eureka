from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type
from data_providers._base import BaseProvider
from models._base import BaseStruct
from models.context import ExecutionContext


class BaseWriter[T: BaseStruct](ABC):
    """Writes data to datbase."""

    @abstractmethod
    def provider(self) -> BaseProvider[T]: ...

    @abstractmethod
    def _validate_input(self, context: ExecutionContext,
                        struct: T,
                        old_struct: T | None,
                        deleting: bool) -> None:
        if deleting:
            assert old_struct is not None, f"trying to delete non-existing {struct.type_name()}."

    def sync(self, struct: T, context: ExecutionContext) -> None:
        """Sync a struct with the database."""
        with context:
            context.log(f'syncing {struct.type_name()}.')
            found_struct = self.provider().find(struct.identity())
            if found_struct is not None: struct = found_struct.intersect(struct)
            self._validate_input(context, struct, found_struct, False)
            if found_struct is None:
                context.transaction.sql(struct.db_table_name()).insert(struct.to_record())
                context.log(f'added {struct}.')
            else:
                context.transaction.sql(struct.db_table_name()).update(struct.to_record(), found_struct.to_record())
                context.log(f'changes: {struct.changes_since(found_struct)}')
            context.log(f'synced {struct.type_name()}.')

    def remove(self, struct: T, context: ExecutionContext) -> None:
        """Override to remove a struct from the database."""
        with context:
            context.log(f'removing {struct.type_name()}.')
            found_struct = self.provider().find(struct)
            self._validate_input(context, struct, found_struct, True)
            context.transaction.sql(struct.db_table_name()).delete(found_struct.to_record())
            context.log(f'removed {struct.type_name()}.')