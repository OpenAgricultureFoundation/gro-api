from django.apps import AppConfig
from cityfarm_api.models import DynamicOptions
from cityfarm_api.utils.state import system_layout

class LayoutConfig(AppConfig):
    name = 'layout'
    def ready(self):
        from . import  monkey_patch_resolvers
        # Use DynamicOptions for dynamic models
        dynamic_fields = []
        dynamic_models = set()
        for model in self.get_models():
            all_fields = model._meta._get_fields(
                reverse=False, include_parents=False
            )
            for field in all_fields:
                if getattr(field, 'is_dynamic', False):
                    dynamic_fields.append(field)
                    dynamic_models.add(model)
        for field in dynamic_fields:
            for layout in system_layout.allowed_values:
                with system_layout.as_value(layout):
                    if field.rel.to and not isinstance(field.rel.to, str):
                        dynamic_models.add(field.rel.to)
        for model in dynamic_models:
            model._meta.__class__ = DynamicOptions
