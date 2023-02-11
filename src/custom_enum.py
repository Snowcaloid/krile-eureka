from typing import Any
from enum import Enum

class CustomEnum(str, Enum):
    """
    Utility class which can be subclassed to create enums using auto().
    Also provides utility methods for common enum operations.
    """

    @classmethod
    def _missing_(cls, enum_value: Any):
        ## Ref: https://stackoverflow.com/a/60174274/4900327
        ## This is needed to allow Pydantic to perform case-insensitive conversion to AutoEnum.
        return cls.from_str(enum_value=enum_value, raise_error=True)

    def _generate_next_value_(name, start, count, last_values):
        return name

    @property
    def str(self) -> str:
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.__class__.__name__ + '.' + self.name)

    def __eq__(self, other):
        return self is other