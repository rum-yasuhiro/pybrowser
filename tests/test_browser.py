import unittest
from test.support import captured_stdout
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
        
    def test_show(self):
        with captured_stdout() as stdout:
            show("<body>abcdefg</body>")
        self.assertEqual(stdout.getvalue(), "abcdefg")