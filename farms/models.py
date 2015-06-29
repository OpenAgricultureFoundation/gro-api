from slugify import slugify
from django.db import models
from solo.models import SingletonModel
from django.core.exceptions import ValidationError
from layout.schemata import all_schemata

LAYOUT_CHOICES = ((key, val.name) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])


def layout_validator(value):
    if value not in LAYOUT_CHOICES:
        raise ValidationError("{} is not a valid layout".format(value))


class Farm(SingletonModel):
    farm_id = models.IntegerField(null=True, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    root_server = models.URLField(default="http://cityfarm.media.mit.edu")
    ip = models.GenericIPAddressField(null=True)
    layout = models.SlugField(choices=LAYOUT_CHOICES,
                              validators=[layout_validator, ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_layout = self.layout

    def save(self, *args, **kwargs):
        # TODO: Flush DB, Stop the server, makemigrations, migrate, and restart
        # the server whenever the value of layout is changed in a leaf node

        # If a slug has not been provided, generate one based on the name
        if not self.slug:
            self.slug = slugify(self.name.lower())
        return super().save(*args, **kwargs)
        # If the layout has been changed, clear the layout database, and tell
        # the control server to refresh
        if self.layout != self._original_layout:
            pass

all_models = [Farm]
