from dataclasses import dataclass
from typing import Callable, Optional
from data.db.sql import Transaction
from models.permissions import Permissions
from utils.logger import BaseLogger


ContextResponse = Callable[[str, Exception], None]


@dataclass
class ExecutionContext:
    """Context for executing operations.

    Usage:
    ```python
    with context:
        # Check permissions if there are any required for the operation.
        context.assert_permissions(required_permissions)
        # Log messages to the context. They are collected and flushed at
        # the end of the context if the context is exited without an exception.
        context.log("This is something that went well.)
        # If the assertion fails, it will raise an error and flush the provided message.
        assert needed_condition, "This is something that went wrong."
    ```
    """
    user_id: int
    guild_id: int
    logger: BaseLogger
    """Handles logging."""
    on_flush: Optional[ContextResponse] = None #type: ignore
    """Event handler for additional actions when the log is flushed."""
    permissions: Optional[Permissions] = None
    """Current permissions of the context."""
    _message: str = ''
    _level: int = 0
    _transaction: Transaction = None #type: ignore

    def __enter__(self):
        if self._level > 0:
            self.transaction.__enter__()

        self._level += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._level -= 1
        if self._level <= 0:
            self.transaction.__exit__(exc_type, exc_value, traceback)
            self._level = 0
            if exc_type is not None:
                self.log(f"FATAL - an error occured: {exc_value}")
            self.logger.flush(self._message, exc_type)
        elif exc_type is not None:
            raise

    def log(self, message: str):
        self._message += message + '\n'

    def assert_permissions(self, permissions: Permissions) -> None:
        assert self.permissions is not None, "context dict must have permissions set for this action."
        self.permissions.full_check(permissions)

    @property
    def transaction(self) -> Transaction:
        if self._transaction is None:
            self._transaction = Transaction()
        return self._transaction