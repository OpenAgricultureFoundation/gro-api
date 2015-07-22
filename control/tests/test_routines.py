import logging
from django.test import TestCase
from control.commands import Command
from control.routines import Routine

command_count = 0

class TestCommand(Command):
    def run(self):
        global command_count
        command_count += 1
        self.returncode = 0
        return
        yield

class RoutineTestCase(TestCase):
    def test_valid_routine(self):
        global command_count
        command_count = 0
        class TestRoutine(Routine):
            command_classes = [TestCommand, TestCommand]
        result = TestRoutine().to_json()
        self.assertEqual(len(result), 2)
        for subresult in result:
            self.assertEqual(subresult['title'], 'Unnamed Command')
            self.assertEqual(subresult['log'], '')
            self.assertEqual(subresult['error'], '')
            self.assertEqual(subresult['returncode'], 0)

    def test_invalid_routine(self):
        class TestRoutine(Routine):
            command_classes = [TestCommand, str]
        self.assertRaises(TypeError, TestRoutine.check)

