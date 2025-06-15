from typing import Type, override
from models.button import ButtonStruct
from data_providers._base import BaseProvider


class ButtonsProvider(BaseProvider[ButtonStruct]):
    @override
    def struct_type(self) -> Type[ButtonStruct]:
        return ButtonStruct