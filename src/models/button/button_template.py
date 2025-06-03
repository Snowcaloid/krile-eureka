from typing import override
from models.button.discord_button import DiscordButton
from utils.basic_types import ButtonType


from centralized_data import PythonAsset, PythonAssetLoader
from discord import Interaction


from abc import abstractmethod


class ButtonTemplate(PythonAsset):
    @classmethod
    def base_asset_class_name(cls): return 'ButtonTemplate'

    @abstractmethod
    def button_type(self) -> ButtonType: ...

    @abstractmethod
    async def callback(self, interaction: Interaction, button: DiscordButton): ...


class ButtonTemplates(PythonAssetLoader[ButtonTemplate]):
    @override
    def asset_folder_name(self) -> str:
        return 'buttons'

    def get(self, button_type: ButtonType) -> ButtonTemplate:
        return next(template for template in self.loaded_assets if template.button_type() == button_type)