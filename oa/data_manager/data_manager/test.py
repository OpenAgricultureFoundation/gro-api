import random
import inspect
import logging
import unittest
import itertools
from slugify import slugify
from collections import defaultdict
from django.conf import settings
from django.test.runner import DiscoverRunner
from django.utils.functional import cached_property
from rest_framework import test
from .utils import system_layout
from ..farms.models import Farm
from ..layout.schemata import all_schemata
from ..control.routines import Reset

class APITestCase(test.APITestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        testMethod = getattr(self, methodName)
        self.layouts = getattr(testMethod, 'layouts', None)
        if self.layouts is None and settings.SERVER_TYPE == settings.ROOT:
            raise ValueError(
                "Cannot run test %s.%s in a root server because no layout "
                "is specified" % (self.__class__, methodName)
            )

    def shortDescription(self):
        suffix = "(with layout {})".format(system_layout.current_value)
        desc = super().shortDescription()
        if desc is None:
            return suffix
        else:
            return desc + " " + suffix

    @cached_property
    def url_prefix(self):
        if settings.SERVER_TYPE == settings.LEAF:
            return ''
        else:
            return '/{}-farm'.format(system_layout.current_value)

    def url_for_object(self, resource_name, resource_id=None):
        url = '{}/{}/'.format(self.url_prefix, resource_name)
        if resource_id is not None:
            url += '{}/'.format(resource_id)
        return url


class TestSuite(unittest.TestSuite):
    def __init__(self, tests=()):
        self.unconfigured_tests = []
        self.configured_tests = defaultdict(list)
        self.addTests(tests)

    def __iter__(self):
        return itertools.chain(iter(self.unconfigured_tests), *(iter(tests) for
            tests in self.configured_tests.values()))

    def countTestCases(self):
        cases = 0
        for test in self.unconfigured_tests:
            cases += test.countTestCases()
        for layout, tests in self.configured_tests:
            for test in tests:
                cases += test.countTestCases()
        return cases

    def addTest(self, test):
        if not callable(test):
            raise TypeError("The test to add must be callable")
        if (inspect.isclass(test) and
                issubclass(test, (unittest.TestCase, unittest.TestSuite))):
            raise TypeError("TestCases and TestSuites must be instantiated "
                            "before passing them to addTest()")
        if isinstance(test, APITestCase) and test.layouts is not None:
            for layout in test.layouts:
                self.configured_tests[layout].append(test)
        else:
            self.unconfigured_tests.append(test)

    def run_unconfigured_tests(self, result):
        print('\nRunning tests on unconfigured farm')
        for test in self.unconfigured_tests:
            if result.shouldStop:
                break
            test(result)
        return result

    def run_configured_tests(self, layout, result):
        print('\nRunning tests on %s farm' % layout)
        for test in self.configured_tests[layout]:
            if result.shouldStop:
                break
            test(result)
        return result

    def run(self, result):
        self.run_unconfigured_tests(result)
        if result.shouldStop:
            return result
        for layout in self.configured_tests.keys():
            Reset()()
            farm = Farm.get_solo()
            farm.name = "{} farm".format(layout)
            farm.layout = layout
            farm.save()
            self.run_configured_tests(layout, result)
            if result.shouldStop:
                break
        return result

    def debug_unconfigured_tests(self):
        for test in self.unconfigured_tests:
            test.debug()

    def debug_configured_tests(self, layout):
        for test in self.configured_tests[layout]:
            test.debug()

    def debug(self):
        self.debug_unconfigured_tests()
        for layout in self.configured_tests.keys():
            Reset()()
            farm = Farm.get_solo()
            farm.name = "{} farm".format(layout)
            farm.layout = layout
            farm.save()
            self.debug_configured_tests(layout)


class TestLoader(unittest.TestLoader):
    suiteClass = TestSuite


class TestRunner(DiscoverRunner):
    test_suite = TestSuite
    test_loader = TestLoader()

    def setup_databases(self):
        with system_layout.as_value(None):
            return super().setup_databases()


def run_with_layouts(*layouts):
    def wrapper(f, layouts=layouts):
        f.layouts = layouts
        return f
    return wrapper


def run_with_any_layout(f):
    if not hasattr(run_with_any_layout, 'possible_layouts'):
        run_with_any_layout.possible_layouts = list(all_schemata.keys())
    f.layouts = [random.choice(run_with_any_layout.possible_layouts),]
    return f

run_with_all_layouts = run_with_layouts(*all_schemata.keys())
