from os import path
import os
from typing import Any, Callable
import venv

LAMBDA_PATH = path.abspath(path.join(path.dirname(__file__), '..', 'lambda'))
LAMBDA_FILENAME = 'lambda_function.py'
VENV_NAME = '.venv'
LAMBDA_HANDLER = 'lambda_handler'
DIST_PATH = path.abspath(path.join(path.dirname(__file__), '..', 'dist'))

log = lambda *values, end='\n', sep=' ': print('\033[30m', *values, '\033[0m', end=end, sep=sep)
info = lambda *values, end='\n', sep=' ': print('\033[36m', *values, '\033[0m', end=end, sep=sep)
warn = lambda *values, end='\n', sep=' ': print('\033[33m', *values, '\033[0m', end=end, sep=sep)
error = lambda *values, end='\n', sep=' ': print('\033[31m', *values, '\033[0m', end=end, sep=sep)

def try_create_venv(at='./'):
    venv_path = os.path.join(os.path.abspath(at), VENV_NAME)
    rel_venv_path = os.path.relpath(venv_path, LAMBDA_PATH).replace('\\', '/')
    if not os.path.exists(venv_path):
        log(f"Creating virtual environment at {rel_venv_path}...")
        venv.create(venv_path, with_pip=True)
        log(f"Created virtual environment at {rel_venv_path}")
    return (venv_path, rel_venv_path)

def apply_to_all(fn: Callable[[str], Any]):
    for dir in [entry.name for entry in os.scandir(LAMBDA_PATH) if entry.is_dir()]:

        dirpath = os.path.abspath(os.path.join(LAMBDA_PATH, dir))

        is_lambda = 'function.py' in [
            entry.name for entry in os.scandir(dirpath) if entry.is_file()
        ]

        if is_lambda:
            fn(dirpath)