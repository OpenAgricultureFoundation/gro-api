#!/usr/bin/env python
import os
import tempfile
from django.test import TestCase
import control.exceptions
import control.commands


class CommandTestCase(TestCase):
    def test_command(self):
        command = control.commands.Command()
        self.assertEqual(command.title, 'Unnamed Command')
        self.assertRaises(NotImplementedError, command.run)


class FifoCommandTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_fifo_fd, cls.mock_fifo_path = tempfile.mkstemp()
        cls.FirstCommand = control.commands.FifoCommand('First', '1')
        cls.SecondCommand = control.commands.FifoCommand('Second', '2')
        cls.ThirdCommand = control.commands.FifoCommand('Third', '3')

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.mock_fifo_path)

    def setUp(self):
        control.commands.fifo_path = self.mock_fifo_path
        os.ftruncate(self.mock_fifo_fd, 0)

    def test_command_creation(self):
        test_command = self.FirstCommand()
        self.assertEqual(test_command.title, 'First')
        self.assertFalse(hasattr(test_command, 'returncode'))

    def test_single_command_once(self):
        test_command = self.FirstCommand()
        list(test_command.run())
        with open(self.mock_fifo_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, '1')
        self.assertEqual(test_command.returncode, 0)

    def test_single_command_repeated(self):
        test_command = self.FirstCommand()
        [list(test_command.run()) for i in range(5)]
        with open(self.mock_fifo_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, '11111')
        self.assertEqual(test_command.returncode, 0)

    def test_multiple_commands_once(self):
        test_command_1 = self.FirstCommand()
        test_command_2 = self.SecondCommand()
        test_command_3 = self.ThirdCommand()
        list(test_command_1.run())
        list(test_command_2.run())
        list(test_command_3.run())
        with open(self.mock_fifo_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, '123')
        self.assertEqual(test_command_1.returncode, 0)
        self.assertEqual(test_command_2.returncode, 0)
        self.assertEqual(test_command_3.returncode, 0)

    def test_multiple_commands_repeated(self):
        test_command_1 = self.FirstCommand()
        test_command_2 = self.SecondCommand()
        test_command_3 = self.ThirdCommand()
        [list(test_command_1.run()) for i in range(2)]
        [list(test_command_2.run()) for i in range(2)]
        [list(test_command_3.run()) for i in range(2)]
        [list(test_command_1.run()) for i in range(3)]
        [list(test_command_2.run()) for i in range(3)]
        [list(test_command_3.run()) for i in range(3)]
        with open(self.mock_fifo_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, '112233111222333')
        self.assertEqual(test_command_1.returncode, 0)
        self.assertEqual(test_command_2.returncode, 0)
        self.assertEqual(test_command_3.returncode, 0)

    def test_invalid_fifo_file(self):
        control.commands.fifo_path = "/invalid/fifo/path"
        command = self.FirstCommand()
        try:
            list(command.run())
        except control.exceptions.InvalidFifoPath as e:
            self.assertEquals(
                e.message,
                'FIFO file "/invalid/fifo/path" does not exist'
            )
        else:
            self.fail('InvalidFifoPath exception not thrown')


class ManagerCommandsTestCase(TestCase):
    success_manager_code = b"""#!/usr/bin/env python3
import sys
print('Ran command "{}"'.format(' '.join(sys.argv)))
"""

    failure_manager_code = b"""#!/usr/bin/env python3
import sys
sys.exit('Failed to run command "{}"'.format(' '.join(sys.argv)))
"""

    @classmethod
    def setUpClass(cls):
        cls.mock_success_fd, cls.mock_success_path = tempfile.mkstemp()
        os.write(cls.mock_success_fd, cls.success_manager_code)
        cls.mock_failure_fd, cls.mock_failure_path = tempfile.mkstemp()
        os.write(cls.mock_failure_fd, cls.failure_manager_code)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.mock_success_path)
        os.remove(cls.mock_failure_path)

    def activate_success_manager(self):
        control.commands.manager_path = self.mock_success_path

    def activate_failure_manager(self):
        control.commands.manager_path = self.mock_failure_path

    def test_command_creation(self):
        command = control.commands.ManagerCommand('Test', '')()
        self.assertEqual(command.title, 'Test')
        self.assertFalse(hasattr(command, 'returncode'))

    def test_successful_command_single_argument(self):
        self.activate_success_manager()
        command = control.commands.ManagerCommand('Command', 'arg1')()
        line_count = 0
        expected_output = 'Ran command "{} arg1"\n'.format(
            self.mock_success_path
        )
        line_count = 0
        for line in command.run():
            line_count += 1
            self.assertLessEqual(line_count, 1)  # There should only be 1 line
            self.assertEqual(line, expected_output)
            self.assertFalse(line.is_error)
        self.assertEqual(command.returncode, 0)

    def test_successful_command_multiple_arguments(self):
        self.activate_success_manager()
        command = control.commands.ManagerCommand('Command', 'arg1', '--flag')()
        line_count = 0
        expected_output = 'Ran command "{} arg1 --flag"\n'.format(
            self.mock_success_path
        )
        line_count = 0
        for line in command.run():
            line_count += 1
            self.assertLessEqual(line_count, 1)  # There should only be 1 line
            self.assertEqual(line, expected_output)
            self.assertFalse(line.is_error)
        self.assertEqual(command.returncode, 0)

    def test_failed_command_single_argument(self):
        self.activate_failure_manager()
        command = control.commands.ManagerCommand('Command', 'arg1')()
        line_count = 0
        expected_output = 'Failed to run command "{} arg1"\n'.format(
            self.mock_failure_path
        )
        for line in command.run():
            line_count += 1
            self.assertLessEqual(line_count, 1)  # There should only be 1 line
            self.assertEqual(line, expected_output)
            self.assertTrue(line.is_error)
        self.assertEqual(command.returncode, 1)

    def test_failed_command_multiple_arguments(self):
        self.activate_failure_manager()
        command = control.commands.ManagerCommand('Command', 'arg1', '--flag')()
        line_count = 0
        expected_output = 'Failed to run command "{} arg1 --flag"\n'.format(
            self.mock_failure_path
        )
        for line in command.run():
            line_count += 1
            self.assertLessEqual(line_count, 1)  # There should only be 1 line
            self.assertEqual(line, expected_output)
            self.assertTrue(line.is_error)
        self.assertEqual(command.returncode, 1)

    def test_invalid_manager_file(self):
        control.commands.manager_path = "/invalid/manager/path"
        command = control.commands.ManagerCommand('Test', 'arg1')()
        try:
            list(command.run())
        except control.exceptions.InvalidManagerPath as e:
            self.assertEquals(
                e.message,
                'manage.py file "/invalid/manager/path" does not exist'
            )
        else:
            self.fail('InvalidManagerPath exception not thrown')
