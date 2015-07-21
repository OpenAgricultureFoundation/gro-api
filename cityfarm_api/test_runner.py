import logging
from django.test.runner import DiscoverRunner
from .utils.state import system_layout

class TestRunner(DiscoverRunner):
    def setup_databases(self):
        with system_layout.as_value(None):
            return super().setup_databases()
    def run_tests(self, *args, **kwargs):
        logging.disable(logging.ERROR)
        super().run_tests(*args, **kwargs)
