import unittest
import os
from utils import shell

class TestVenv(unittest.TestCase):

    def setUp(self):
        self.venv = os.getenv('VIRTUAL_ENV')
        cwd = os.getcwd()
        self.cwd = os.path.abspath(os.path.join(cwd,'..'))

    def test_venv_is_running(self):
        '''ensure registered venv is this project'''
        assert(self.cwd in self.venv)

    def test_correct_python(self):
        '''test python is from project venv'''
        pystr = shell('which python')
        assert(self.venv in pystr)

