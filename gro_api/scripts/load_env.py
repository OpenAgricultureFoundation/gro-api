#!/usr/bin/env python3
import os

def load_env():
    if getattr(load_env, 'loaded', False):
        return

    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    os.environ['GRO_API_SERVER_TYPE'] = 'leaf'
    os.environ['GRO_API_SERVER_MODE'] = 'production'
    os.environ['UWSGI_MASTER_FIFO'] = '/etc/openag_fifo'

    load_env.loaded = True

if __name__ == '__main__':
    load_env()
