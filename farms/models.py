from django.db import models
from solo.models import SingletonModel
from layout.schemata import all_schemata


class Farm(SingletonModel):
    farm_id = models.IntegerField(null=True)
    root_server = models.URLField(default="http://cityfarm.media.mit.edu")
    name = models.CharField(max_length=100)
    subdomain = models.SlugField(null=True)
    LAYOUT_CHOICES = ((key, val["name"]) for key, val in all_schemata.items())
    layout = models.SlugField(choices=LAYOUT_CHOICES)
    ip = models.GenericIPAddressField(null=True)

    def is_configured(self):
        return bool(self.farm_id)
