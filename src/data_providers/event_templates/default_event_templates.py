from centralized_data import YamlAssetLoader
from models.event_template.data import EventTemplateData


from typing import Type, override


class DefaultEventTemplates(YamlAssetLoader[EventTemplateData]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def constructor(self):
        super().constructor()
        self.loaded_assets.sort(key=lambda template: template.autocomplete_weight())

    @override
    def asset_class(self) -> Type[EventTemplateData]: return EventTemplateData

    @override
    def asset_folder_name(self):
        return 'event_templates'