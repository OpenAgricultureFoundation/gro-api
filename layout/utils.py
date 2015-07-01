from django.conf import settings
from cityfarm_api.utils import get_current_layout
from .schemata import all_schemata

def schemata_to_use():
    if settings.SERVER_TYPE == settings.LEAF:
        layout = get_current_layout()
        return {layout: all_schemata[layout]}
    else:
        return all_schemata
