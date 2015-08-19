from django.core.cache import caches
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Clear the relevent caches when flushing the DB'

    def handle(self, *args, **kwargs):
        from oa.data_manager.farms.models import Farm
        caches['default'].delete(Farm.get_cache_key())
        from oa.data_manager.layout.models import Enclosure
        caches['default'].delete(Enclosure.get_cache_key())
        from oa.data_manager.data_manager.utils import system_layout
        system_layout.clear_cache()
