from django.db import models
from django.db.migrations.state import ModelState
from django.db.migrations.operations.base import Operation
from django.db.migrations.operations.models import CreateModel
from django.db.migrations.operations.fields import AlterField
from django.utils.functional import cached_property
from layout.state import SystemLayout
from layout.models import dynamic_models
from layout.schemata import all_schemata

class CreateDynamicModels(Operation):
    """
    This operation should only be performed when a layout is first selected in a
    farm being configured for the first time. It creates all of the models for
    the selected layout and modifies the `Tray` model to point to the correct
    model. It cannot be run in reverse.
    """
    reversible = False

    @cached_property
    def operations(self):
        ops = []
        if SystemLayout().current_value is None:
            return []
        schema = all_schemata[SystemLayout().current_value]
        created_models = set()
        created_models.add('Enclosure')
        def create_model(entity):
            model = dynamic_models[entity.name]
            model_state = ModelState.from_model(model)
            # TODO: Check this against `MigrationAutodetector.generate_created_models`
            ops.append(CreateModel(
                name=model_state.name,
                fields=model_state.fields,
                options=model_state.options,
                bases=model_state.bases,
                managers=model_state.managers
            ))
            created_models.add(entity.name)
        for entity in schema.dynamic_entities.values():
            if not entity.parent in created_models:
                create_model(schema.dynamic_entities[entity.parent])
            if not entity.name in created_models:
                create_model(entity)
        to_model = 'layout.%s' % schema.entities['Tray'].parent
        ops.append(AlterField(
            'tray', 'parent',
            models.ForeignKey(to=to_model, related_name='children')
        ))
        return ops

    def state_forwards(self, app_label, state):
        for operation in self.operations:
            operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        for operation in self.operations:
            operation.database_forwards(
                app_label, schema_editor, from_state, to_state
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        raise NotImplementedError()
