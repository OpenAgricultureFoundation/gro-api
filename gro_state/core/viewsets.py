from rest_framework.mixins import (
    RetrieveModelMixin, UpdateModelMixin, ListModelMixin
)
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.status import HTTP_201_CREATED

class SingletonModelViewSet(RetrieveModelMixin,
                            UpdateModelMixin,
                            ListModelMixin,
                            GenericViewSet):
    pass

class BulkModelViewSet(ModelViewSet):
    def create(self, request, *args, **kwargs):
        many = request.query_params.get('many', False)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers
        )
