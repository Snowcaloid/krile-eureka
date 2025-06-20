

from typing import override
from data_providers._base import BaseProvider
from models.event_template import EventTemplateStruct


class EventTemplateProvider(BaseProvider[EventTemplateStruct]):
    from data_providers.event_templates.default_event_templates import DefaultEventTemplates
    @DefaultEventTemplates.bind
    def _default_templates(self) -> DefaultEventTemplates: ...

    @override
    def struct_type(self) -> type[EventTemplateStruct]:
        return EventTemplateStruct

    @override
    def find(self, struct: EventTemplateStruct) -> EventTemplateStruct:
        custom_template = super().find(struct)
        if custom_template is not None: return custom_template
        data = next(
            (
                template for template in self._default_templates.loaded_assets
                if template.type == struct.event_type
            ), None
        )
        if data is None: return None #type: ignore
        return EventTemplateStruct(
            event_type=data.type,
            data=data
        )