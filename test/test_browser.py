import unittest
from browser import *


class TestBrowser(unittest.TestCase):

    def test_parse_url(self):
        self.assertEqual(
            parse_url("http://example.org/index.html"), ("http", "example.org", "/index.html"))
        self.assertEqual(
            parse_url("http://example.org"), ("http", "example.org", "/"))

    def test_request(self):
        header, body = request("http://example.org/index.html")
        self.assertEqual(header["content-type"], "text/html; charset=UTF-8")