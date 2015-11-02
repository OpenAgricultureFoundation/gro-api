from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.exceptions import APIException
from ..farms.models import Farm

def get_layout_from_farm(slug):
    if slug is None:
        return None
    cache = caches['default']
    cache_key = '{}_layout'.format(slug)
    layout = cache.get(cache_key)
    if layout is None:
        try:
            layout = Farm.objects.get(slug=slug).layout
        except ObjectDoesNotExist as e:
            raise Http404()
    return res

def get_farm_from_request(request):
    if 'FARM_SLUG' in request.environ:
        return request.environ['FARM_SLUG']
    if 'FARM_SLUG' in request.GET:
        return request.GET['FARM_SLUG']
    return None
