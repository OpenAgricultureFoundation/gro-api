"""
This module defines a single model :class:`Farm` that represents an instance of
a CityFARM. This module handles the logic for contacting the remote server when
the farm is created and settings a farm layout.
"""
import socket
import tortilla
from slugify import slugify
from django.db import models
from django.conf import settings
from solo.models import SingletonModel
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

from cityfarm_api.models import Model
from layout.schemata import all_schemata
from control.routines import Restart

LAYOUT_CHOICES = ((key, val.name) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])
DEFAULT_LAYOUT = 'tray'
UNCONFIGURED_NAME = 'Unconfigured'
UNCONFIGURED_SLUG = slugify(UNCONFIGURED_NAME.lower())


def layout_validator(value):
    if value not in LAYOUT_CHOICES:
        raise ValidationError("{} is not a valid layout".format(value))

if settings.SERVER_TYPE == settings.LEAF:
    RootIdField = models.IntegerField
    root_id_kwargs = {
        'editable': False,
        'null': True
    }
if settings.SERVER_TYPE == settings.ROOT:
    RootIdField = models.AutoField
    root_id_kwargs = {
        'primary_key': True
    }

class Farm(Model, SingletonModel):
    root_id = RootIdField(**root_id_kwargs)
    name = models.CharField(
        max_length=100, blank=(settings.SERVER_TYPE == settings.LEAF),
        default=UNCONFIGURED_NAME
    )
    slug = models.SlugField(
        max_length=100, blank=(settings.SERVER_TYPE == settings.LEAF),
        unique=True
    )
    root_server = models.URLField(
        default="http://cityfarm.media.mit.edu", null=True
    )
    ip = models.GenericIPAddressField(
        editable=(settings.SERVER_TYPE == settings.ROOT),
        null=(settings.SERVER_TYPE == settings.LEAF)
    )
    layout = models.SlugField(
        choices=LAYOUT_CHOICES, default=DEFAULT_LAYOUT,
        validators=[layout_validator, ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_slug = self.slug
        self._old_layout = self.layout

    @property
    def is_configured(self):
        return self.slug and self.slug != UNCONFIGURED_SLUG

    def clean(self):
        if settings.SERVER_TYPE == settings.LEAF:
            if not self.is_configured:
                self.slug = slugify(self.name.lower())
            self.check_network()

    def check_network(self):
        url_to_check = self.root_server or '8.8.8.8'
        if self.root_server:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((urlparse(url_to_check).netloc, 80))
            self.ip = sock.getsockname()[0]

    def save(self, *args, **kwargs):
        self.clean()
        if settings.SERVER_TYPE == settings.LEAF:
            return self.leaf_save(*args, **kwargs)
        else:
            return self.root_save(*args, **kwargs)

    def leaf_save(self, *args, **kwargs):
        """ This save function is used for leaf servers """
        root_api = tortilla.wrap(self.root_server, debug=True)
        if self.is_configured:
            # Register this farm with the root server
            if settings.SERVER_MODE == settings.DEVELOPMENT:
                # Jk, don't actually contact the server, just pretend we did
                self.root_id = 1
                super().save(*args, **kwargs)
            else:
                # Actually contact the server
                data = {field.name: getattr(self, field.name) for field in
                        self._meta.fields}
                data.pop(self._meta.pk.name)
                if self.root_id:
                    res = root_api.farms(self.root_id).put(data=data)
                else:
                    res = root_api.farms.post(data=data)
                assert res.status_code == 200
                # TODO: Update any parameters on the model that were
                # rejected or modified by the root server
                super().save(*args, **kwargs)
        if self.layout != self._old_layout:
            Restart().to_json()

    def root_save(self, *args, **kwargs):
        """ This save function is used for root servers """
        # TODO: Set up database mirroring here
        super().save(*args, **kwargs)
