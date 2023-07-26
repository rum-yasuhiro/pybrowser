import unittest
from test.support import captured_stdout
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
from browser import *


class TestBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # サーバーを立ち上げる
        cls.server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        # サーバーが立ち上がるまで少し待つ (時間がかかる場合は適宜調整)
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        # サーバーをシャットダウンする
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    
    def test_parse_url(self):
        self.assertEqual(
            parse_url("http://example.org/index.html"), ("http", "example.org", "/index.html"))
        self.assertEqual(
            parse_url("http://example.org"), ("http", "example.org", "/"))

    def test_request(self):
        header, body = request("http://localhost/tests/index.html")
        self.assertEqual(body, "<body><h1>Test</h1></body>")
        
    def test_show(self):
        with captured_stdout() as stdout:
            show("<body>abcdefg</body>")
        self.assertEqual(stdout.getvalue(), "abcdefg")