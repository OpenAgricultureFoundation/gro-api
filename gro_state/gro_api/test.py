import random
import inspect
import logging
import unittest
import itertools
from slugify import slugify
from unittest.suite import _DebugResult
from collections import defaultdict
from django.conf import settings
from django.core.management import call_command
from django.test.runner import DebugSQLTextTestResult, DiscoverRunner
from django.utils.functional import cached_property
from rest_framework.test import APITestCase
from .utils.layout import system_layout
from ..farms.models import Farm
from ..layout.schemata import all_schemata

class APITestCase(APITestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        testMethod = getattr(self, methodName)
        if not hasattr(testMethod, 'layouts'):
            raise ValueError(
                'Cannot run test {}.{} becasue no layout is specified'.format(
                    self.__class__.__name__, methodName
                )
            )
        self.layouts = testMethod.layouts

    @cached_property
    def url_prefix(self):
        if settings.SERVER_TYPE == settings.LEAF:
            return ''
        else:
            return '/{}-farm'.format(self.layout)

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
        if isinstance(test, APITestCase):
            for layout in test.layouts:
                if layout is not None:
                    self.configured_tests[layout].append(test)
                else:
                    self.unconfigured_tests.append(test)
        else:
            self.unconfigured_tests.append(test)

    def run_test(self, test, result, debug):
        self._handleClassSetUp(test, result)
        if not debug:
            test(result)
        else:
            test.debug()
        self._tearDownPreviousClass(test, result)
        result._previousTestClass = test.__class__

    def run_unconfigured_tests(self, result, debug):
        result.stream.writeln('\nRunning tests on unconfigured farm')
        for test in self.unconfigured_tests:
            if result.shouldStop:
                break
            call_command('clear_caches')
            self.run_test(test, result, debug)
        return result

    def run_configured_tests(self, layout, result, debug):
        result.stream.writeln('\nRunning tests on {} farm'.format(layout))
        for test in self.configured_tests[layout]:
            if result.shouldStop:
                break
            call_command('clear_caches')
            self.run_test(test, result, debug)
        return result

    def run(self, result, debug=False):
        self.run_unconfigured_tests(result, debug)
        if result.shouldStop:
            return result
        for layout in self.configured_tests.keys():
            call_command('flush', interactive=False)
            call_command('migrate', interactive=False)
            farm = Farm.get_solo()
            farm.name = "{} farm".format(layout)
            farm.layout = layout
            farm.save()
            self.run_configured_tests(layout, result, debug)
            if result.shouldStop:
                break
        return result

    def debug(self):
        debug = _DebugResult()
        self.run(debug, True)


class TestLoader(unittest.TestLoader):
    suiteClass = TestSuite


class LayoutTextTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        if self.showAll:
            self.stream.writeln('ok')
        else:
            self.stream.write('.')

    def addError(self, test, err):
        self.errors.append((
            test, self._exc_info_to_string(err, test),
            system_layout.current_value
        ))
        if self.showAll:
            self.stream.writeln('ERROR')
        else:
            self.stream.write('E')

    def addFailure(self, test, err):
        self.failures.append((
            test, self._exc_info_to_string(err, test),
            system_layout.current_value
        ))
        if self.showAll:
            self.stream.writeln('FAIL')
        else:
            self.stream.write('F')

    def printErrorList(self, flavour, errors):
        for test, err, layout in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("{}: {} (with layout {})".format(
                flavour, self.getDescription(test), layout
            ))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)


class LayoutDebugSQLTextTestResult(DebugSQLTextTestResult,
                                   LayoutTextTestResult):
    pass


class TestRunner(DiscoverRunner):
    test_suite = TestSuite
    test_loader = TestLoader()

    def setup_databases(self):
        with system_layout.as_value(None):
            return super().setup_databases()

    def get_resultclass(self):
        if self.debug_sql:
            return LayoutDebugSQLTextTestResult
        else:
            return LayoutTextTestResult


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
