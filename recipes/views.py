from rest_framework.viewsets import ModelViewSet
from .models import Recipe, RecipeRun, SetPoint
from .serializers import (
    RecipeSerializer, RecipeRunSerializer, SetPointSerializer
)

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class RecipeRunViewSet(ModelViewSet):
    queryset = RecipeRun.objects.all()
    serializer_class = RecipeRunSerializer


class SetPointViewSet(ModelViewSet):
    queryset = SetPoint.objects.all()
    serializer_class = SetPointSerializer
