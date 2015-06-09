from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Runs the control server'
    def add_arguments(self, parser):
        parser.add_argument('-p', '--port', dest='port', type=int, default=8080,
            help='The port on which to run the control server')
        parser.add_argument('-f', '--fifo', '--fifo-path', dest='fifo',
            help='Filepath of the Master FIFO of the CityFARM API server')
        parser.add_argument('-m', '--manager', '--manager-path', dest='manager',
            help='Filepath of the Django Manager of the CityFARM API server')
    def handle(self, *args, **kwargs):
        from control.server import app
        if 'fifo' in kwargs:
            app.fifo_path = kwargs['fifo']
        if 'manager' in kwargs:
            app.manager_path = kwargs['manager']
        app.run('127.0.0.1', port=kwargs['port'])
