from cityfarm_api.serializers import model_serializers
from cityfarm_api.viewsets import SingletonViewSet, model_viewsets
from .models import Enclosure

class EnclosureViewSet(SingletonViewSet):
    model = Enclosure
