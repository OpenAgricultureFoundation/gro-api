from django.db import models
from cityfarm_api.models import Model
from layout.models import PlantSite

class PlantType(Model):
    common_name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)
    size_choices = (
        ('short-leafy', 'Short Leafy'),
        ('short-branchy', 'Short Branchy'),
        ('medium-leafy', 'Medium Leafy'),
        ('medium-branchy', 'Medium Branchy'),
        ('tall-leafy', 'Tall Leafy'),
        ('tall-branchy', 'Tall Barnchy')
    )
    plant_size = models.CharField(max_length=100, choices=size_choices)
    def __str__(self):
        return self.common_name

class Plant(Model):
    plant_type = models.ForeignKey(PlantType, related_name='plants')
    site = models.OneToOneField(PlantSite, related_name='plant')
    sown_date = models.DateTimeField()
