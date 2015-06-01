from django.db import models
from farms.models import Farm
from layout.models import all_models

# TODO This won't work on root. Use a generic foreignkey field and select the
# queryset in serializers.py
tray_class = all_models[Farm.get_solo().layout]["tray"]
class PlantSite(models.Model):
    parent = models.ForeignKey(tray_class, related_name="plant_sites")
    row = models.IntegerField()
    col = models.IntegerField()
    def __str__(self):
        return "{} (r={}, c={})".format(str(self.parent), self.row, self.col)

class PlantType(models.Model):
    common_name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)
    def __str__(self):
        return self.common_name

class Plant(models.Model):
    type = models.ForeignKey(PlantType)
    site = models.ForeignKey(PlantSite, related_name="plant")
