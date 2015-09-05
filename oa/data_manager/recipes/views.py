from rest_framework.viewsets import ModelViewSet
from .models import Recipe, RecipeRun, SetPoint, ActuatorOverride
from .serializers import (
    RecipeSerializer, RecipeRunSerializer, SetPointSerializer,
    ActuatorOverrideSerializer
)

class RecipeViewSet(ModelViewSet):
    """ A recipe uploaded by a user that can be run on a tray """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class RecipeRunViewSet(ModelViewSet):
    """ An instance of a recipe being run on a tray """
    queryset = RecipeRun.objects.all()
    serializer_class = RecipeRunSerializer


class SetPointViewSet(ModelViewSet):
    """
    A desired value for a resource property at a given time for a recipe run
    """
    queryset = SetPoint.objects.all()
    serializer_class = SetPointSerializer


class ActuatorOverrideViewSet(ModelViewSet):
    """ A state to which to set an actuator for a specific period in time """
    queryset = ActuatorOverride.objects.all()
    serializer_class = ActuatorOverrideSerializer
