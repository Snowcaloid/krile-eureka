

from typing import override
from data_providers._base import BaseProvider
from models.event_template import EventTemplateStruct


class EventTemplateProvider(BaseProvider[EventTemplateStruct]):
    from data_providers.event_templates.default_event_templates import DefaultEventTemplates
    @DefaultEventTemplates.bind
    def _default_templates(self) -> DefaultEventTemplates: ...

    @override
    def db_table_name(self) -> str:
        return 'event_templates'

    @override
    def find(self, struct: EventTemplateStruct) -> EventTemplateStruct:
        custom_template = super().find(struct)
        if custom_template is not None: return custom_template
        return next(
            (
                template for template in self._default_templates.loaded_assets
                if template.type == struct.event_type
            ),
            None
        ) # type: ignore