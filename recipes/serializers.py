from rest_framework.exceptions import APIException
from cityfarm_api.serializers import BaseSerializer
from .models import RecipeRun, SetPoint

class RecipeRunSerializer(BaseSerializer):
    model = RecipeRun

    def create(self, validated_data):
        recipe = validated_data['recipe']
        recipe_file = recipe.file
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise APIException(
            'Recipe runs can only be created and deleted. To change what the '
            'recipe will do, either edit the set points manually or delete '
            'this run and start a new one.'
        )
