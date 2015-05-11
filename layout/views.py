from django.shortcuts import render
from layout.schemata import schemata_to_use
from layout.models import all_models
from layout.serializers import all_serializers
from rest_framework import viewsets, generics, mixins
from cityfarm_api.viewsets import SingletonViewSet
from solo.models import SingletonModel

all_viewsets = {}
for schema_name, schema in schemata_to_use().items():
    curr_viewsets = {}
    model_names = [entity["name"] for entity in schema["entities"]]
    model_names += ["tray", "enclosure"]
    for model_name in model_names:
        curr_model = all_models[schema_name][model_name]
        if issubclass(curr_model, SingletonModel):
            viewset_classes = (SingletonViewSet,)
        else:
            viewset_classes = (viewsets.ModelViewSet,)
        class ViewSet(*viewset_classes):
            model = curr_model
            queryset = all_models[schema_name][model_name].objects.all()
            serializer_class = all_serializers[schema_name][model_name]
        curr_viewsets[model_name] = ViewSet
    all_viewsets[schema_name] = curr_viewsets
