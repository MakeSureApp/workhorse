import unittest
import app as tested_app
import json

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        tested_app.app.config['TESTING'] = True
        self.app = tested_app.app.test_client()

    def test_get_hello_endpoint(self):
        r = self.app.get('/')
        self.assertEqual(r.data, b'Server is loaded...')

    def test_post_hello_endpoint(self):
        r = self.app.post('/')
        self.assertEqual(r.status_code, 405)


if __name__ == '__main__':
    unittest.main()
