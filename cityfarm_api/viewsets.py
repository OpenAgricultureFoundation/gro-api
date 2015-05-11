from rest_framework import viewsets, mixins

class SingletonViewSet(viewsets.GenericViewSet,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin):
    def list(self, request, *args, **kwargs):
        self.model.get_solo()
        return super().list(request, *args, **kwargs)
