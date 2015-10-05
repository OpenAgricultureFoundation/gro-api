from django.apps import AppConfig
from ..gro_api.models import DynamicOptions
from ..gro_api.utils.layout import system_layout
from .schemata import all_schemata

class LayoutConfig(AppConfig):
    name = 'gro_api.layout'
    def ready(self):
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

        # Disable mocking of SystemLayout from settings.SETUP_WITH_LAYOUT
        system_layout.use_mock_value = False
        system_layout.mock_value = None

        # Delete the content types for all of the entities that we can't
        # encounter if they exist
        from django.contrib.contenttypes.models import ContentType
        from .models import dynamic_models
        for layout in all_schemata.keys():
            for entity in all_schemata[layout].dynamic_entities.values():
                if entity.name not in dynamic_models:
                    ContentType.objects.filter(
                        app_label='layout', model=entity.name.lower()
                    ).delete()

    def setup_initial_data(self):
        from django.contrib.auth.models import Group
        from django.contrib.contenttypes.models import ContentType
        from .models import dynamic_models
        layout_editors_group = Group.objects.get(name='LayoutEditors')
        for model in dynamic_models.values():
            content_type = ContentType.objects.get_for_model(model)
            for permission in content_type.permission_set.all():
                if not permission.codename.startswith('delete'):
                    layout_editors_group.permissions.add(permission)

    data_dependencies = ['control',]
