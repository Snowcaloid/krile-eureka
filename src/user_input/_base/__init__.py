
from abc import ABC, abstractmethod

from centralized_data import Bindable
from models._base import BaseStruct

class SimpleUserInput[T](Bindable, ABC):
    """
    Base class for simple user input validation and fixing.
    When creating new user input classes, inherit from this class
    and override `validate_and_fix()`.
    The user input can be bound to a service.
    """

    @abstractmethod
    def validate_and_fix(self, value: any) -> T: ...
    """Override to add assertions and user input fixing logic."""

class BaseUserInput[T: BaseStruct](Bindable, ABC):
    """
    Base class for user input validation and fixing.
    When creating new user input classes, inherit from this class,
    set the T-Type to the struct type and override:
    * `validate_and_fix()`
    * `can_insert()`
    * `can_update()`
    * `can_remove()`
    The user input can be bound to a service.
    """

    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @abstractmethod
    def can_insert(self, struct: T) -> bool: ...
    """Override to check if the struct can be inserted into the database."""

    @abstractmethod
    def can_update(self, struct: T) -> bool: ...
    """Override to check if the struct can be updated in the database."""

    @abstractmethod
    def can_remove(self, struct: T) -> bool: ...
    """Override to check if the struct can be removed from the database."""