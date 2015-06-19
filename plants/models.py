from django.db import models
from farms.models import Farm
from layout.models import Tray

class PlantSite(models.Model):
    parent = models.ForeignKey(Tray, related_name="plant_sites")
    row = models.IntegerField()
    col = models.IntegerField()
    def __str__(self):
        return "{} (r={}, c={})".format(str(self.parent), self.row, self.col)

class PlantType(models.Model):
    common_name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)
    size_choices = (('short-leafy', 'Short Leafy'),
        ('short-branchy', 'Short Branchy'),
        ('medium-leafy', 'Medium Leafy'),
        ('medium-branchy', 'Medium Branchy'),
        ('tall-leafy', 'Tall Leafy'),
        ('tall-branchy', 'Tall Barnchy'))
    plant_size = models.CharField(max_length=100, choices=size_choices)
    def __str__(self):
        return self.common_name

class Plant(models.Model):
    plant_type = models.ForeignKey(PlantType, related_name='plants')
    site = models.ForeignKey(PlantSite, related_name="plant")
    sown_date = models.DateTimeField()
