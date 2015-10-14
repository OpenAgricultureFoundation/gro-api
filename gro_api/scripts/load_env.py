#!/usr/bin/env python3
import os
import shelve

def load_env():
    if getattr(load_env, 'loaded', False):
        return

    base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    env_vars_path = os.path.join(base_path, 'env_vars')

    env_vars = shelve.open(env_vars_path)
    try:
        for key, val in env_vars.items():
            os.environ[key] = val
        env_vars.close()
    except Exception as e:
        pass
    load_env.loaded = True

if __name__ == '__main__':
    load_env()
