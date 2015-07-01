import env
import socket
import tortilla
from slugify import slugify
from django.db import models
from django.conf import settings
from solo.models import SingletonModel
from django.core.exceptions import ValidationError

from layout.schemata import all_schemata

LAYOUT_CHOICES = ((key, val.name) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])
DEFAULT_LAYOUT = 'tray'
UNCONFIGURED = 'unconfigured'


def layout_validator(value):
    if value not in LAYOUT_CHOICES:
        raise ValidationError("{} is not a valid layout".format(value))


class Farm(SingletonModel):
    name = models.CharField(
        max_length=100, blank=(settings.SERVER_TYPE == settings.LEAF),
        default=UNCONFIGURED
    )
    slug = models.SlugField(
        max_length=100, blank=(settings.SERVER_TYPE == settings.LEAF),
        unique=True, primary_key=(settings.SERVER_TYPE == settings.ROOT)
    )
    root_server = models.URLField(default="http://cityfarm.media.mit.edu")
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
        self._original_layout = self.layout

    @property
    def root_api(self):
        return tortilla.wrap(self.root_server, debug=True)

    @property
    def is_configured(self):
        return self.name != UNCONFIGURED and self.slug != UNCONFIGURED

    def clean(self):
        if settings.SERVER_MODE == settings.LEAF:
            if not self.slug:
                self.slug = slugify(self.name.lower())
            self.check_network()

    def check_network(self):
        # Put this in a separate function so that we can call it as a cron job
        # It should only be called from clean though
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.root_server, 80))
        self.ip = s.getsockname()[0]
        print(self.ip)

    def save(self, *args, **kwargs):
        if settings.SERVER_TYPE == settings.LEAF:
            return self.leaf_save(*args, **kwargs)
        else:
            return self.root_save(*args, **kwargs)

    def leaf_save(self, *args, **kwargs):
        if self.is_configured:
            self.root_api.farms[self.slug].put(data=self)
        res = super().save(*args, **kwargs)
        if self.layout != self._original_layout:
            # Restart the server so the new models can load
            url = env['UWSGI_HTTP'] + '/restart'
            requests.get(url)
        return res

    def root_save(self, *args, **kwargs):
        # TODO: Set up database mirroring here
        return super().save(*args, **kwargs)
