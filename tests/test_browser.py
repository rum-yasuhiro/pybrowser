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
            URL("http://example.org/index.html").parse_url(), ("http", "example.org", "/index.html", None))
        self.assertEqual(
            URL("http://example.org").parse_url(), ("http", "example.org", "/", None))
        self.assertEqual(
            URL("http://example.org:80").parse_url(), ("http", "example.org", "/", 80))

    def test_request_with_http(self):
        with open("./tests/index.html") as file:
            test_body = file.read()  
        header, body = URL("http://localhost:8000/tests/index.html").request()
        self.assertEqual(body, test_body)
        
    def test_lex(self):
        test_body = "<body><h1>Test</h1></body>"
        token_list = Browser().lex(body=test_body)
        self.assertEqual(token_list[0].tag, "body")
        self.assertEqual(token_list[1].tag, "h1")
        self.assertEqual(token_list[2].text, "Test")
        self.assertEqual(token_list[3].tag, "/h1")
        self.assertEqual(token_list[4].tag, "/body")
        
    def test_layout(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        token_list = Browser().lex(body=test_body)
        display_list = Browser().layout(token_list=token_list)
        
        self.assertEqual(display_list[0][2], "Test")
        self.assertEqual(display_list[0][3].configure()["family"], 'None')
        self.assertEqual(display_list[0][3].configure()["size"], 20)
        self.assertEqual(display_list[0][3].configure()["weight"], "normal")
        self.assertEqual(display_list[0][3].configure()["slant"], "roman")
        self.assertEqual(display_list[0][3].configure()["underline"], 0)
        self.assertEqual(display_list[0][3].configure()["overstrike"], 0)
        
        # イタリック体
        self.assertEqual(display_list[1][2], "Italic")
        self.assertEqual(display_list[1][3].configure()["family"], 'None')
        self.assertEqual(display_list[1][3].configure()["size"], 20)
        self.assertEqual(display_list[1][3].configure()["weight"], "normal")
        self.assertEqual(display_list[1][3].configure()["slant"], "italic")
        self.assertEqual(display_list[1][3].configure()["underline"], 0)
        self.assertEqual(display_list[1][3].configure()["overstrike"], 0)
        
        # ボールド体
        self.assertEqual(display_list[2][2], "Bold")
        self.assertEqual(display_list[2][3].configure()["family"], 'None')
        self.assertEqual(display_list[2][3].configure()["size"], 20)
        self.assertEqual(display_list[2][3].configure()["weight"], "bold")
        self.assertEqual(display_list[2][3].configure()["slant"], "roman")
        self.assertEqual(display_list[2][3].configure()["underline"], 0)
        self.assertEqual(display_list[2][3].configure()["overstrike"], 0)
        
        # ノーマル
        self.assertEqual(display_list[3][2], "Normal")
        self.assertEqual(display_list[3][3].configure()["family"], 'None')
        self.assertEqual(display_list[3][3].configure()["size"], 20)
        self.assertEqual(display_list[3][3].configure()["weight"], "normal")
        self.assertEqual(display_list[3][3].configure()["slant"], "roman")
        self.assertEqual(display_list[3][3].configure()["underline"], 0)
        self.assertEqual(display_list[3][3].configure()["overstrike"], 0)