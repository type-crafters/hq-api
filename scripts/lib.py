from os import path

LAMBDA_PATH = path.abspath(path.join(path.dirname(__file__), '..', 'lambda'))
LAMBDA_FILENAME = 'lambda_function.py'
LAMBDA_HANDLER = 'lambda_handler'
DIST_PATH = path.abspath(path.join(path.dirname(__file__), '..', 'dist'))

log = lambda *values, end='\n', sep=' ': print('\033[30m', *values, '\033[0m', end=end, sep=sep)
info = lambda *values, end='\n', sep=' ': print('\033[36m', *values, '\033[0m', end=end, sep=sep)
warn = lambda *values, end='\n', sep=' ': print('\033[33m', *values, '\033[0m', end=end, sep=sep)
error = lambda *values, end='\n', sep=' ': print('\033[31m', *values, '\033[0m', end=end, sep=sep)