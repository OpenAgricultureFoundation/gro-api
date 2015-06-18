#!/usr/bin/env python
import os
import sys
import tempfile
from django.test import TestCase
import control.commands
from control.models import *
from control.commands import *
from control.exceptions import *


class CommandTestCase(TestCase):
    def test_command(self):
        command = Command()
        self.assertEqual(command.title, 'Unnamed Command')
        self.assertRaises(NotImplementedError, command.run)

class FifoMixin:
    @classmethod
    def setUpClass(cls):
        cls.old_fifo_path = fifo_path
        cls.mock_fifo_path = os.path.join(tempfile.gettempdir(), 'fifo')
        if os.path.exists(cls.mock_fifo_path):
            os.remove(cls.mock_fifo_path)
        os.mkfifo(cls.mock_fifo_path)

    @classmethod
    def tearDownClass(cls):
        control.commands.fifo_path = cls.old_fifo_path
        os.remove(cls.mock_fifo_path)

    def setUp(self):
        control.commands.fifo_path = self.mock_fifo_path
        os.truncate(self.mock_fifo_path, 0)

    def installInvalidPath(self):
        control.commands.fifo_path = '/invalid/fifo/path'

    def installInvalidFifo(self):
        mock_fifo_fd, control.commands.fifo_path = tempfile.mkstemp()

class FifoCommandTestCase(FifoMixin, TestCase):
    def test_check_invalid_path(self):
        self.installInvalidPath()
        self.assertRaises(InvalidFifoPath, FifoCommand.check)
        errors = check_fifo_path(None)
        self.assertEqual(len(errors), 1)
        expected_message = 'Failed to find FIFO file'
        self.assertEqual(errors[0].msg, expected_message)

    def test_check_invalid_file(self):
        self.installInvalidFifo()
        self.assertRaises(InvalidFifoFile, FifoCommand.check)
        errors = check_fifo_path(None)
        self.assertEqual(len(errors), 1)
        expected_message = 'FIFO file is invalid'
        self.assertEqual(errors[0].msg, expected_message)

    def test_run_not_being_read(self):
        class TestCommand(FifoCommand):
            fifo_command = b't'
        command = TestCommand()
        result = command.to_json()
        self.assertEqual(result['returncode'], 1)

class ReloadWorkersTestCase(FifoMixin, TestCase):
    def test_success(self):
        fifo = os.open(self.mock_fifo_path, os.O_RDONLY | os.O_NONBLOCK)
        command = ReloadWorkers()
        result = command.to_json()
        self.assertEqual(result['title'], 'Reload Workers')
        self.assertEqual(result['returncode'], 0)
        line = os.read(fifo, 1)
        self.assertEqual(line, b'c')
        line = os.read(fifo, 1)
        self.assertEqual(line, b'')

    def test_multiple_success(self):
        fifo = os.open(self.mock_fifo_path, os.O_RDONLY | os.O_NONBLOCK)
        for i in range(5):
            command = ReloadWorkers()
            result = command.to_json()
            self.assertEqual(result['title'], 'Reload Workers')
            self.assertEqual(result['returncode'], 0)
        line = os.read(fifo, 5)
        self.assertEqual(line, b'ccccc')
        line = os.read(fifo, 1)
        self.assertEqual(line, b'')

    def test_failure_not_read(self):
        os.environ['RUN_MAIN'] = 'false'
        command = ReloadWorkers()
        result = command.to_json()
        self.assertEqual(result['returncode'], 1)
        # Simulate running behind Django development server
        os.environ['RUN_MAIN'] = 'true'
        command = ReloadWorkers()
        result = command.to_json()
        self.assertEqual(result['returncode'], 0)

class ShellCommandTestCase(TestCase):
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
        cls.old_manager_path = manager_path
        cls.mock_success_fd, cls.mock_success_path = tempfile.mkstemp()
        os.write(cls.mock_success_fd, cls.success_manager_code)
        cls.mock_failure_fd, cls.mock_failure_path = tempfile.mkstemp()
        os.write(cls.mock_failure_fd, cls.failure_manager_code)

    @classmethod
    def tearDownClass(cls):
        control.commands.manager_path = cls.old_manager_path
        os.remove(cls.mock_success_path)
        os.remove(cls.mock_failure_path)

    def activate_success_manager(self):
        control.commands.manager_path = self.mock_success_path

    def activate_failure_manager(self):
        control.commands.manager_path = self.mock_failure_path

    def test_successful_command(self):
        self.activate_success_manager()
        class TestCommand(ManagerCommand):
            args = ('arg1',)
        line_count = 0
        expected_output = 'Ran command "{} arg1"\n'.format(
            self.mock_success_path
        )
        result = TestCommand().to_json()
        self.assertEqual(result['log'], expected_output)
        self.assertEqual(result['error'], '')
        self.assertEqual(result['returncode'], 0)

    def test_failed_command(self):
        self.activate_failure_manager()
        class TestCommand(ManagerCommand):
            args = ('arg1',)
        line_count = 0
        expected_output = 'Failed to run command "{} arg1"\n'.format(
            self.mock_failure_path
        )
        result = TestCommand().to_json()
        self.assertEqual(result['log'], expected_output)
        self.assertEqual(result['error'], expected_output)
        self.assertEqual(result['returncode'], 1)

    def test_invalid_manager_file(self):
        control.commands.manager_path = "/invalid/manager/path"
        command = Migrate()
        self.assertRaises(InvalidManagerPath, command.to_json)
        errors = check_manager_path(None)
        self.assertEqual(len(errors), 1)
        expected_message = 'Failed to find manage.py file'
        self.assertEqual(errors[0].msg, expected_message)
