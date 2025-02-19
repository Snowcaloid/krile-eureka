from __future__ import annotations
from abc import abstractmethod
from functools import wraps
from typing import Callable, Dict, List, Self, Type, override

class DataProvider:
    _providers: Dict[Type[DataProvider], DataProvider] = {}

    def __new__(cls) -> Self:
        if DataProvider._providers.get(cls.provider_name()) is None:
            DataProvider._providers[cls.provider_name()] = super().__new__(cls)
        return DataProvider._providers[cls.provider_name()]

    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_initialized'):
            self.constructor(*args, **kwargs)
            self._initialized = True

    @abstractmethod
    def constructor(self) -> None: pass

    @property
    def ready(self) -> bool:
        return hasattr(self, '_initialized') and self._initialized

    @classmethod
    def bind(cl, func: Callable[[Self], DataProvider], safe: bool = True) -> property:
        """
           Transform the method into a property that returns the Provider.

           This method is only necessery for DataProviders that require other DataProviders to function,
           in which case, a central method should be responsible for instantiating the required providers.

           ### Parameters
           `safe`: `default=True` The provider can be instatiated without any problems. One of the reasons you may want
           to have an unsafe binding is if you're (for whatever reason) copying values from one provider to the other.
           Seriously, you have access to the other provider via the property. Just use it...
        """
        @wraps(func)
        def wrapper(instance: Self):
            if safe:
                return cl()
            return DataProvider._providers.get(cl)
        return property(wrapper)
