import os

cwd = os.getcwd()
venv = os.getenv('VIRTUAL_ENV')

print cwd, venv
