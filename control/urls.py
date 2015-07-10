from django.conf.urls import url
from .views import all_views

def init_router(router):
    for name, view in all_views.items():
        view_url = url(r'^{}/$'.format(name), view, name=name)
        router.add_api_view(name, view_url)
