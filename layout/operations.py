from django.db import models
from django.db.migrations.state import ModelState
from django.db.migrations.operations.base import Operation
from django.db.migrations.operations.models import CreateModel
from django.db.migrations.operations.fields import AlterField
from cityfarm_api.utils.state import system_layout
from layout.models import dynamic_models, ParentField
from layout.schemata import all_schemata


class CreateDynamicModels(Operation):
    """
    This operation should only be performed when a layout is first selected in
    a farm being configured for the first time. It creates all of the models
    for the selected layout and modifies the `Tray` model to point to the
    correct model. It cannot be run in reverse.
    """
    reduces_to_sql = True

    @property
    def operations(self):
        ops = []
        if system_layout.current_value is None:
            return []
        schema = all_schemata[system_layout.current_value]
        created_models = set()
        created_models.add('Enclosure')

        def create_model(entity):
            model = dynamic_models[entity.name]
            model_state = ModelState.from_model(model)
            ops.append(CreateModel(
                name=model_state.name,
                fields=model_state.fields,
                options=model_state.options,
                bases=model_state.bases,
                managers=model_state.managers
            ))
            created_models.add(entity.name)

        for entity in schema.dynamic_entities.values():
            # Make sure the model's parent has already been created so that the
            # db contraints on the `parent` field don't complain
            if entity.parent not in created_models:
                create_model(schema.dynamic_entities[entity.parent])
            if entity.name not in created_models:
                create_model(entity)
        tray_to_model = 'layout.%s' % schema.entities['Tray'].parent
        ops.append(AlterField(
            'tray', 'parent', ParentField(model_name='Tray')
        ))
        return ops

    def state_forwards(self, app_label, state):
        for operation in self.operations:
            operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state,
                          to_state):
        for operation in self.operations:
            operation.database_forwards(
                app_label, schema_editor, from_state, to_state
            )

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        for operation in self.operations:
            operation.database_backwards(
                app_label, schema_editor, from_state, to_state
            )

    def describe(self):
        return "Creating dynamic models for system layout {}".format(
            system_layout.current_value
        )
