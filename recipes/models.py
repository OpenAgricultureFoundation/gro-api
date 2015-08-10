import time
from django.db import models
from cityfarm_api.models import Model
from layout.models import Tray
from plants.models import PlantType
from resources.models import ResourceProperty


class Recipe(Model):
    name = models.CharField(max_length=100)
    plant_type = models.ManyToManyField(PlantType, related_name='recipes')
    file = models.FileField(upload_to="recipes")

    def __str__(self):
        return self.name


class RecipeRun(Model):
    recipe = models.ForeignKey(Recipe, related_name='runs')
    tray = models.ForeignKey(Tray, related_name='recipe_runs+')
    start_timestamp = models.IntegerField(blank=True, default=time.time)
    end_timestamp = models.IntegerField(editable=False)


class SetPoint(Model):
    class Meta:
        get_latest_by = 'timestamp'

    tray = models.ForeignKey(Tray, related_name='set_points+')
    property = models.ForeignKey(ResourceProperty, related_name='set_points+')
    timestamp = models.IntegerField()
    value = models.FloatField()
    recipe_run = models.ForeignKey(RecipeRun, related_name='set_points+')
