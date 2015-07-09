from cityfarm_api.viewsets import SingletonViewSet
from .models import Enclosure

class EnclosureViewSet(SingletonViewSet):
    model = Enclosure
