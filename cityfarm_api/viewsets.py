from rest_framework.mixins import (
    RetrieveModelMixin, UpdateModelMixin, ListModelMixin
)
from rest_framework.viewsets import GenericViewSet

class SingletonModelViewSet(RetrieveModelMixin,
                            UpdateModelMixin,
                            ListModelMixin,
                            GenericViewSet):
    pass
