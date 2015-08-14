from .views import (
    SensorTypeViewSet, SensorViewSet, SensingPointViewSet, DataPointViewSet
)

def contribute_to_router(router):
    router.register(r'sensorType', SensorTypeViewSet)
    router.register(r'sensor', SensorViewSet)
    router.register(r'sensingPoint', SensingPointViewSet)
    router.register(r'dataPoint', DataPointViewSet)
