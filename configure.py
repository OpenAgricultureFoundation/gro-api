#!/usr/bin/env python3
import os
import shelve
import argparse

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dev', '-d', dest='development', default=False,
        help='Run in development mode'
    )
    parser.add_argument(
        '--root', '-r', dest='root', default=False, help='Run a root server'
    )
    args = parser.parse_args()

    folder_path = os.path.dirname(os.path.realpath(__file__))

    with shelve.open(os.path.join(folder_path, 'env_vars')) as env_vars:
        env_vars['DJANGO_SETTINGS_MODULE'] = 'cityfarm_api.settings'
        env_vars['CITYFARM_API_ROOT'] = folder_path

        if args.development:
            env_vars['CITYFARM_API_SERVER_MODE'] = 'development'
            env_vars['UWSGI_PROCESSES'] = '1'
            env_vars['UWSGI_MASTER_FIFO'] = os.path.join(folder_path, 'fifo')
            env_vars['UWSGI_HTTP'] = '127.0.0.1:8000'
        else:
            env_vars['CITYFARM_API_SERVER_MODE'] = 'production'
            env_vars['UWSGI_PROCESSES'] = '4'
            env_vars['UWSGI_MASTER_FIFO'] = '/etc/cityfarm_api_fifo'
            env_vars['UWSGI_HTTP'] = '0.0.0.0:80'

        if args.root:
            env_vars['CITYFARM_API_SERVER_TYPE'] = 'root'
        else:
            env_vars['CITYFARM_API_SERVER_TYPE'] = 'leaf'

if __name__ == '__main__':
    configure()
