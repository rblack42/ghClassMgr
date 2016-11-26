import unittest
from ghcm import create_app
from ghcm.config import DevConfig

class TestURLs(unittest.TestCase):

    def setUp(self):
        app = create_app(DevConfig)
        self.client = app.test_client()

    def test_rerurn_code(self):
        result = self.client.get('/')
        assert(result.status_code == 200)

