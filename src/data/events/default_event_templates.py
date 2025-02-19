from asset_loader import YamlAssetLoader
from data.events.event_template import EventTemplate


from typing import Type, override


class DefaultEventTemplates(YamlAssetLoader[EventTemplate]):
    @override
    def constructor(self):
        super().constructor()
        self.loaded_assets.sort(key=lambda template: template.autocomplete_weight())

    @override
    def asset_class(self) -> Type[EventTemplate]: return EventTemplate

    @override
    def asset_folder_name(self):
        return 'event_templates'