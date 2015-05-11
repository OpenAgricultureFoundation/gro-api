from cityfarm_api.serializers import TreeSerializer
from layout.models import all_models
from layout.models import DimensionsMixin, CoordinatesMixin

all_serializers = {}
for schema_name, curr_models in all_models.items():
    curr_serializers = {}
    for model_name, model in curr_models.items():
        class Serializer(TreeSerializer):
            class Meta:
                model = model
                depth = 3
        curr_serializers[model_name] = Serializer
    all_serializers[schema_name] = curr_serializers
