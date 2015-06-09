from django.db import models

class Farm(models.Model):
    farm_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    ip = models.GenericIPAddressField(null=True)
    layout = models.SlugField(choices=LAYOUT_CHOICES,
            validators=[layout_validator, ])

