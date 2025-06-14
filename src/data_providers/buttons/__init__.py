from typing import override
from models.button import ButtonStruct
from data_providers._base import BaseProvider


class ButtonsProvider(BaseProvider[ButtonStruct]):
    @override
    def db_table_name(self) -> str:
        return 'buttons'