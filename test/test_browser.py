import unittest
from browser import *


class TestBrowser(unittest.TestCase):

    def test_parse_url(self):
        url1 = "http://example.org/index.html"
        self.assertEqual(
            parse_url(url1), ("http", "example.org", "/index.html"))

        url2 = "http://example.org"
        self.assertEqual(
            parse_url(url2), ("http", "example.org", "/"))
