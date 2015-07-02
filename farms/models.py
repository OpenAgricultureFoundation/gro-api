import env
import socket
import tortilla
from slugify import slugify
from django.db import models
from django.conf import settings
from solo.models import SingletonModel
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

from layout.schemata import all_schemata

LAYOUT_CHOICES = ((key, val.name) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])
DEFAULT_LAYOUT = 'tray'
UNCONFIGURED = 'Unconfigured'


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

class Farm(SingletonModel):
    root_id = RootIdField(**root_id_kwargs)
    name = models.CharField(
        max_length=100, blank=(settings.SERVER_TYPE == settings.LEAF),
        default=UNCONFIGURED
    )
    slug = models.SlugField(
        max_length=100, blank=(settings.SERVER_TYPE == settings.LEAF),
        unique=True
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
        self._old_slug = self.slug
        self._old_layout = self.layout

    def clean(self):
        if settings.SERVER_TYPE == settings.LEAF:
            if not self.slug or self.slug == slugify(UNCONFIGURED.lower()):
                self.slug = slugify(self.name.lower())
            self.check_network()

    def check_network(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((urlparse(self.root_server).netloc, 80))
        self.ip = s.getsockname()[0]

    def save(self, *args, **kwargs):
        self.clean()
        if settings.SERVER_TYPE == settings.LEAF:
            return self.leaf_save(*args, **kwargs)
        else:
            return self.root_save(*args, **kwargs)

    def leaf_save(self, *args, **kwargs):
        is_configured = self.slug and self.slug != slugify(UNCONFIGURED.lower())
        root_api = tortilla.wrap(self.root_server, debug=True)
        if is_configured:
            data = {field.name: getattr(self, field.name) for field in
                    self._meta.fields}
            data.pop(self._meta.pk.name)
            try:
                if self.root_id:
                    res = root_api.farms(self.farm_id).put(data=data)
                else:
                    res = root_api.farms.post(data=data)
                # TODO: Update any parameters on the model that were rejected or
                # modified by the root server
            except Exception as e:
                # TODO: Actually handle these exceptions. For now, we'll just
                # ignore them because we don't actually have a root server to
                # setup things with
                print(e)
        res = super().save(*args, **kwargs)
        if self.layout != self._old_layout:
            print("Restarting")
            # Restart the server so the new models can load
            url = env['UWSGI_HTTP'] + '/restart'
            requests.get(url)
        return res

    def root_save(self, *args, **kwargs):
        # TODO: Set up database mirroring here
        return super().save(*args, **kwargs)
