from django.conf import settings
if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
    from django.contrib.staticfiles.management.commands.runserver import \
            Command as RunserverCommand
else:
    from django.core.management.commands.runserver import \
            Command as RunserverCommand

class Command(RunserverCommand):
    def get_handler(self, *args, **kwargs):
        import layout.monkey_patch_resolvers
        return super().get_handler(self, *args, **kwargs)
