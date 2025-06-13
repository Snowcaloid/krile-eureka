from centralized_data import YamlAssetLoader
from data.events.event_template import EventTemplate


from typing import Type, override

from utils.basic_types import EventType


class DefaultEventTemplates(YamlAssetLoader[EventTemplate]):
    from bot import Bot
    @Bot.bind
    def _bot(self) -> Bot: ...

    @override
    def constructor(self):
        super().constructor()
        self.loaded_assets.sort(key=lambda template: template.autocomplete_weight())
        for guild in self._bot._client.guilds:
            for template in self.loaded_assets:
                EventType.register(guild.id, template.type())

    @override
    def asset_class(self) -> Type[EventTemplate]: return EventTemplate

    @override
    def asset_folder_name(self):
        return 'event_templates'