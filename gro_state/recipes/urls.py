from .views import (
    RecipeViewSet, RecipeRunViewSet, SetPointViewSet, ActuatorOverrideViewSet
)

def contribute_to_router(router):
    router.register('recipe', RecipeViewSet)
    router.register('recipeRun', RecipeRunViewSet)
    router.register('setPoint', SetPointViewSet)
    router.register('actuatorOverride', ActuatorOverrideViewSet)
