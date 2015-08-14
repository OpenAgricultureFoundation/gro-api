from .views import RecipeViewSet, RecipeRunViewSet, SetPointViewSet

def contribute_to_router(router):
    router.register('recipe', RecipeViewSet)
    router.register('recipeRun', RecipeRunViewSet)
    router.register('setPoint', SetPointViewSet)
