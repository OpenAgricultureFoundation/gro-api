from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from ..layout.schemata import all_schemata
from ..gro_api.models import SingletonModel
from ..gro_api.utils.enum import ServerType

LAYOUT_CHOICES = ((key, val.short_description) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])

class Farm(SingletonModel):
    name = models.CharField(
        max_length=100, null=(settings.SERVER_TYPE == ServerType.LEAF),
        help_text='Human readable farm name'
    )
    slug = models.SlugField(
        max_length=100, null=(settings.SERVER_TYPE == ServerType.LEAF),
        help_text='Unique farm identifier'
    )
    layout = models.SlugField(
        choices=LAYOUT_CHOICES, null=(settings.SERVER_TYPE == ServerType.LEAF),
    )

@receiver(post_migrate)
def create_singleton_instance(sender, **kwargs):
    try:
        Farm.get_solo()
    except OperationalError:
        pass
