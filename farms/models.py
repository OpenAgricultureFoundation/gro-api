from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings
from solo.models import SingletonModel
from layout.schemata import all_schemata
import sys
from imp import reload

class Farm(SingletonModel):
    farm_id = models.IntegerField(null=True)
    def is_configured(self):
        return bool(self.farm_id)
    root_server = models.URLField(default="http://cityfarm.media.mit.edu")
    name = models.CharField(max_length=100)
    subdomain = models.SlugField(null=True)
    LAYOUT_CHOICES = ((key, val["name"]) for key,val in all_schemata.items())
    layout = models.SlugField(choices=LAYOUT_CHOICES)
    ip = models.GenericIPAddressField(null=True)
