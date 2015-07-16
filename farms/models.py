"""
This module defines a single model :class:`~farms.models.Farm` that represents
in the abstract a growing device. This module handles the logic for contacting
the remote server when the farm is created and setting a farm layout.
"""
import socket
import tortilla
from slugify import slugify
from urllib.parse import urlparse
from django.db import models
from django.conf import settings
from django.dispatch import Signal
from django.core.exceptions import ValidationError
from solo.models import SingletonModel
from cityfarm_api.models import Model
from layout.schemata import all_schemata

LAYOUT_CHOICES = ((key, val.name) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])
DEFAULT_LAYOUT = 'tray'

farm_bases = (Model,)
if settings.SERVER_TYPE == settings.LEAF:
    RootIdField = models.IntegerField
    root_id_kwargs = {
        'editable': False,
        'null': True
    }
    farm_bases = farm_bases + (SingletonModel,)
if settings.SERVER_TYPE == settings.ROOT:
    RootIdField = models.AutoField
    root_id_kwargs = {
        'primary_key': True
    }

class Farm(*farm_bases):
    """
    This model represents a growing device in the abstract. It is a singleton on
    leaf servers but not on root servers. It also handles the logic of
    registering a farm to a root server when it is configured and sets up the
    database replication and sharding for all of the models.
    """
    class Meta:
        managed = True
    root_id = RootIdField(**root_id_kwargs)
    name = models.CharField(
        max_length=100, null=(settings.SERVER_TYPE == settings.LEAF),
        blank=False
    )
    slug = models.SlugField(
        max_length=100, null=(settings.SERVER_TYPE == settings.LEAF),
        blank=(settings.SERVER_TYPE == settings.LEAF), unique=True
    )
    root_server = models.URLField(
        default="http://cityfarm.media.mit.edu", null=True
    )
    ip = models.GenericIPAddressField(
        editable=(settings.SERVER_TYPE == settings.ROOT),
        null=(settings.SERVER_TYPE == settings.LEAF)
    )
    layout = models.SlugField(
        choices=LAYOUT_CHOICES, null=(settings.SERVER_TYPE == settings.LEAF)
    )

    layout_selected = Signal(providing_args=['layout'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.SERVER_TYPE == settings.LEAF:
            self._old_layout = self.layout

    def clean(self):
        if settings.SERVER_TYPE == settings.LEAF:
            if self.name and not self.slug:
                self.slug = slugify(self.name.lower())
            if self.layout != self._old_layout:
                if self._old_layout:
                    # We can't change from one layout to another; migrating the
                    # database is too hard, and we wouldn't know what to do with
                    # the layout data
                    raise ValidationError(
                        'Changing the layout of a farm is disallowed'
                    )
                else:
                    Farm.layout_selected.send(
                        sender=self.__class__, layout=self.layout
                    )
            self._old_layout = self.layout
            self.check_network()

    def check_network(self):
        """
        Try to open a network connection to the root server. If this fails, try
        to open a connection to Google's root DNS server at '8.8.8.8'. Determine
        the IP address of this machine based on whichever connection is opened
        successfully.
        """
        assert settings.SERVER_TYPE == settings.LEAF, \
            '`check_network` should only be called on leaf servers'
        if self.root_server:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect((urlparse(self.root_server).netloc, 80))
                self.ip = sock.getsockname()[0]
                return
            except socket.gaierror:
                pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((urlparse('8.8.8.8').netloc, 80))
        self.ip = sock.getsockname()[0]

    def save(self, *args, **kwargs):
        if settings.SERVER_TYPE == settings.LEAF:
            return self.leaf_save(*args, **kwargs)
        else:
            return self.root_save(*args, **kwargs)

    def leaf_save(self, *args, **kwargs):
        """ This save function is used for leaf servers """
        root_api = tortilla.wrap(self.root_server, debug=True)
        if self.slug:
            # Register this farm with the root server
            if settings.SERVER_MODE == settings.DEVELOPMENT:
                # Jk, don't actually contact the server, just pretend we did
                self.root_id = 1
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
                for key, val in res.data:
                    if getattr(self, key) != val:
                        setattr(self, key, val)
                # TODO: Update any parameters on the model that were
                # rejected or modified by the root server
        super().save(*args, **kwargs)
        if self.layout != self._old_layout:
            self._old_layout = self.layout

    def root_save(self, *args, **kwargs):
        """ This save function is used for root servers """
        # TODO: Set up database mirroring here
        super().save(*args, **kwargs)
