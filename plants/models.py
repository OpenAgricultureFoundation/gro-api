from django.db import models
from farms.models import Farm
from layout.models import all_models

tray_class = all_models[Farm.get_solo().layout]["tray"]
class PlantSite(models.Model):
    parent = models.ForeignKey(tray_class, related_name="plant_sites")
    row = models.IntegerField()
    col = models.IntegerField()
