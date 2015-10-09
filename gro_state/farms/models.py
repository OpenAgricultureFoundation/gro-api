from slugify import slugify
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.dispatch import receiver
from rest_framework import status
from rest_framework.exceptions import APIException
from ..layout.schemata import all_schemata
from ..gro_state.models import SingletonModel
from ..gro_state.utils import ServerType

LAYOUT_CHOICES = ((key, val.short_description) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])


class Farm(SingletonModel):
    """
    A container for project globals that affect the behavior of the server
    """
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_layout = self.layout
        self._old_slug = self.slug


class LayoutChangeAttempted(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Changing the layout of a farm is not allowed'


class SlugChangeAttempted(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = (
        'Changing the slug of a farm that is connected to a parent server is '
        'not allowed.'
    )


@receiver(pre_save, sender=Farm)
def generate_and_verify_slug(sender, instance, **kwargs):
    # If there is a name and not a slug, generate a slug from the name
    if instance.name and not instance.slug:
        instance.slug = slugify(instance.name.lower())

    # To ensure data integrity, the layout of a farm cannot change once set
    if instance._old_layout and instance.layout != instance._old_layout:
        raise LayoutChangeAttempted()

    # To avoid confusing the parent server, the slug of a farm cannot change
    # once set
    if settings.PARENT_SERVER and instance._old_slug and \
            instance.slug != instance._old_slug:
        raise SlugChangeAttempted()

@receiver(post_save, sender=Farm)
def update_old_values(sender, instance, **kwargs):
    instance._old_layout = instance.layout
    instance._old_slug = instance.slug
    instance.set_to_cache()
