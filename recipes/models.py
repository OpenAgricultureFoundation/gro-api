from django.db import models
from cityfarm_api.models import Model
from layout.models import Tray
from resources.models import ResourceProperty

class SetPoint(Model):
    class Meta:
        get_latest_by = 'timestamp'
    tray = models.ForeignKey(Tray, related_name='set_points+')
    property = models.ForeignKey(ResourceProperty, related_name='set_points+')
    timestamp = models.IntegerField()
    value = models.FloatField()

class Recipe(Model):
    name = models.CharField(max_length=100)
    # TODO: plant_type = GenericForeignKey?
    file = models.FileField(upload_to="recipes")

class RecipeRun(Model):
    recipe = models.ForeignKey(Recipe, related_name='runs')
    start_timestamp = models.IntegerField()
