from .views import (
    ActuatorTypeViewSet, ControlProfileViewSet, ActuatorEffectViewSet,
    ActuatorViewSet, ActuatorStateViewSet
)

def contribute_to_router(router):
    router.register(r'actuatorType', ActuatorTypeViewSet)
    router.register(r'controlProfile', ControlProfileViewSet)
    router.register(r'actuatorEffect', ActuatorEffectViewSet)
    router.register(r'actuator', ActuatorViewSet)
    router.register(r'actuatorState', ActuatorStateViewSet)
