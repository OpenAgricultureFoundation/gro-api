import socket
import logging
import tortilla
from slugify import slugify
from urllib.parse import urlparse
from django.db import models
from django.core.management import call_command
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel
from rest_framework import status
from rest_framework.exceptions import APIException
from cityfarm_api.models import Model
from layout.schemata import all_schemata
from control.routines import SetupLayout

logger = logging.getLogger(__name__)

LAYOUT_CHOICES = ((key, val.name) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])

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


class LayoutChangeAttempted(APIException):
    """
    Changing a farm from one layout is currently not allowed. This exception
    should be raised when a used tries to do that
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('Changing the layout of a farm is disallowed')


class Farm(*farm_bases):
    """
    This model represents a growing device in the abstract. It is a singleton
    on leaf servers but not on root servers. It also handles the logic of
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
        default="http://cityfarm.media.mit.edu",
        null=(settings.SERVER_TYPE == settings.LEAF)
    )
    ip = models.GenericIPAddressField(
        editable=(settings.SERVER_TYPE == settings.ROOT),
        null=(settings.SERVER_TYPE == settings.LEAF)
    )
    layout = models.SlugField(
        choices=LAYOUT_CHOICES, null=(settings.SERVER_TYPE == settings.LEAF)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.SERVER_TYPE == settings.LEAF:
            self._old_layout = self.layout

    def check_network(self):
        """
        Try to open a network connection to the root server. If this fails, try
        to open a connection to Google's root DNS server at '8.8.8.8'.
        Determine the IP address of this machine based on whichever connection
        is opened successfully.
        """
        if not settings.SERVER_TYPE == settings.LEAF:
            logger.error(
                '`check_network` should only be called on leaf servers'
            )
        logger.debug('Checking for network connection')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.root_server:
            address = urlparse(self.root_server).netloc
            logger.debug('Querying server at %s', address)
            try:
                sock.connect((address, 80))
                self.ip = sock.getsockname()[0]
                return
            except socket.gaierror:
                logger.debug('Failed to query server at %s', address)
        address = '8.8.8.8'
        logger.debug('Querying server at %s', address)
        sock.connect((address, 80))
        self.ip = sock.getsockname()[0]

    def save(self, *args, **kwargs):
        if settings.SERVER_TYPE == settings.LEAF:
            return self.leaf_save(*args, **kwargs)
        else:
            return self.root_save(*args, **kwargs)

    def leaf_save(self, *args, **kwargs):
        """ This save function is used for leaf servers """
        if self.name and not self.slug:
            self.slug = slugify(self.name.lower())
            logger.debug(
                'Generated slug "%s" from name "%s"', self.slug, self.name
            )
        if not self.ip:
            self.check_network()
        if self.layout != self._old_layout:
            if self._old_layout:
                raise LayoutChangeAttempted()
            else:
                from cityfarm_api.utils.state import system_layout
                with system_layout.as_value(self.layout):
                    SetupLayout().run()
        self._old_layout = self.layout
        if self.slug:
            # Register this farm with the root server
            if settings.SERVER_MODE == settings.DEVELOPMENT:
                logger.debug('Pretending to contact root server')
                self.root_id = 1
            else:
                root_api = tortilla.wrap(self.root_server, debug=True)
                data = {field.name: getattr(self, field.name) for field in
                        self._meta.fields}
                data.pop(self._meta.pk.name)
                if self.root_id:
                    res = root_api.farms(self.root_id).put(data=data)
                else:
                    res = root_api.farms.post(data=data)
                logger.debug(
                    "Request: %s %s %s", res.request.method, res.request.url,
                    res.request.body
                )
                if res.status_code == 200:
                    for key, val in res.data:
                        if getattr(self, key) != val:
                            setattr(self, key, val)
                else:
                    logger.error(
                        'Root server at "%s" responsed with status code %d, '
                        'body "%s"', self.root_server, res.status_code,
                        res.data
                    )
        super().save(*args, **kwargs)
        if self.layout != self._old_layout:
            self._old_layout = self.layout

    def root_save(self, *args, **kwargs):
        """ This save function is used for root servers """
        # TODO: Set up database mirroring here
        super().save(*args, **kwargs)
