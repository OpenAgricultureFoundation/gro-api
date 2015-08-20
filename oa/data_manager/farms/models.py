import socket
import logging
import tortilla
from slugify import slugify
from urllib.parse import urlparse
from requests.exceptions import ConnectionError
from django.db import models
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from ..control.commands import Migrate, ReloadWorkers, LoadInitialData
from ..layout.schemata import all_schemata

logger = logging.getLogger(__name__)

LAYOUT_CHOICES = ((key, val.description) for key, val in all_schemata.items())
LAYOUT_CHOICES = sorted(LAYOUT_CHOICES, key=lambda choice: choice[0])

if settings.SERVER_TYPE == settings.LEAF:
    from django.core.cache import caches
    RootIdField = models.IntegerField
    root_id_kwargs = {
        'editable': False,
        'null': True
    }
    from ..data_manager.models import SingletonModel as FarmBase
else:
    RootIdField = models.AutoField
    root_id_kwargs = {
        'primary_key': True
    }
    FarmBase = models.Model


class SlugChangeAttempted(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = (
        'Changing the slug of a farm that has already been registered to a '
        'root server is not allowed.'
    )


class LayoutChangeAttempted(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Changing the layout of a farm is not allowed.'


class RootServerConnectionRefused(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        'Failed to contact root server. Farm could not be registered.'
    )


class RootServerMessageRejected(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        'Failed to register farm with root server.'
    )


class Farm(FarmBase):
    root_id = RootIdField(**root_id_kwargs)
    name = models.CharField(
        max_length=100, null=(settings.SERVER_TYPE == settings.LEAF),
        help_text='Human readable farm name'
    )
    slug = models.SlugField(
        max_length=100, null=(settings.SERVER_TYPE == settings.LEAF),
        blank=(settings.SERVER_TYPE == settings.LEAF), unique=True,
        help_text='Unique farm identifier'
    )
    root_server = models.URLField(
        default="http://openag.media.mit.edu",
        null=(settings.SERVER_TYPE == settings.LEAF),
        help_text='URL of the root server to which this farm is registered'
    )
    ip = models.GenericIPAddressField(
        editable=(settings.SERVER_TYPE == settings.ROOT),
        null=(settings.SERVER_TYPE == settings.LEAF),
        help_text='The current IP address of this farm'
    )
    layout = models.SlugField(
        choices=LAYOUT_CHOICES, null=(settings.SERVER_TYPE == settings.LEAF),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.SERVER_TYPE == settings.LEAF:
            self._old_layout = self.layout
            self._old_slug = self.slug

    def check_network(self):
        """
        Try to open a network connection to the root server. If this fails,
        open a connection to Google's root DNS server at '8.8.8.8'.  Determine
        the IP address of this machine based on whichever connection is opened
        successfully. This should only fail if we are running without iternet.
        """
        if not settings.SERVER_TYPE == settings.LEAF:
            logger.error(
                '`check_network` should only be called on leaf servers'
            )
            return
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
        if self.root_id and self.slug != self._old_slug:
            raise SlugChangeAttempted()
        if not self.ip:
            self.check_network()
        if self.layout != self._old_layout:
            if self._old_layout:
                raise LayoutChangeAttempted()
            else:
                Migrate('layout', '0001')()
                from ..data_manager.utils import system_layout
                with system_layout.as_value(self.layout):
                    Migrate()()
                LoadInitialData()()
                system_layout.clear_cache()
        if not self.root_id and self.slug and self.root_server and self.layout:
            # Register this farm with the root server
            if settings.SERVER_MODE == settings.DEVELOPMENT:
                logger.debug('Pretending to contact root server')
                self.root_id = 1
            else:
                root_api = tortilla.wrap(self.root_server, debug=True)
                data = {field.name: getattr(self, field.name) for field in
                        self._meta.fields}
                data.pop(self._meta.pk.name)
                try:
                    if not self.root_id:
                        res = root_api.farms.post(data=data)
                except ConnectionError:
                    raise RootServerConnectionRefused()
                if res.status_code == 200:
                    for key, val in res.data:
                        if getattr(self, key) != val:
                            setattr(self, key, val)
                else:
                    # TODO: Make this message more readable
                    raise RootServerMessageRejected(
                        'Root server at "{}" responsed with status code {}, '
                        'body "{}"'.format(self.root_server, res.status_code,
                        res.data)
                    )
        super().save(*args, **kwargs)
        self._old_slug = self.slug
        if self.layout != self._old_layout:
            self._old_layout = self.layout
            ReloadWorkers()()

    def root_save(self, *args, **kwargs):
        """ This save function is used for root servers """
        # TODO: Set up database mirroring here
        super().save(*args, **kwargs)


@receiver(post_migrate)
def create_singleton_instance(sender, **kwargs):
    try:
        Farm.get_solo()
    except OperationalError:
        pass
