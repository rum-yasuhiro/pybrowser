import unittest
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
from browser import Browser
from html_parser import Element, Text, HTMLParser
from url import URL


class TestBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # サーバーを立ち上げる
        cls.server = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
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

    def test_load(self):
        test_url = "http://localhost:8000/tests/index.html"
        Browser().load(test_url)

    def test_magnify(self):
        test_url = "http://localhost:8000/tests/index.html"
        browser = Browser()
        browser.load(test_url)
        expected_font_size = 16
        self.assertEqual(browser.display_list[1].font["size"], expected_font_size)
        for _ in range(4):
            browser.magnify(None)
            expected_font_size += 4
            self.assertEqual(browser.display_list[1].font["size"], expected_font_size)
        # 最大フォントサイズより大きくならないかどうか
        browser.magnify(None)
        self.assertEqual(
            browser.display_list[1].font["size"], browser.document.maximum_font_size
        )

    def test_reduce(self):
        expected_font_size = 16
        test_url = "http://localhost:8000/tests/index.html"
        browser = Browser()
        browser.load(test_url)
        expected_font_size = 16

        self.assertEqual(browser.display_list[1].font["size"], expected_font_size)
        for _ in range(3):
            browser.reduce(None)
            expected_font_size -= 4
            self.assertEqual(browser.display_list[1].font["size"], expected_font_size)
        # 最小フォントサイズより小さくならないかどうか
        browser.reduce(None)
        self.assertEqual(
            browser.display_list[1].font["size"], browser.document.minimum_font_size
        )


class TestURL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # サーバーを立ち上げる
        cls.server = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
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
            URL("http://example.org/index.html").parse_url(),
            ("http", "example.org", "/index.html", None),
        )
        self.assertEqual(
            URL("http://example.org").parse_url(), ("http",
                                                    "example.org", "/", None)
        )
        self.assertEqual(
            URL("http://example.org:80").parse_url(), ("http",
                                                       "example.org", "/", 80)
        )

    def test_request_with_http(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        header, body = URL("http://localhost:8000/tests/index.html").request()
        self.assertEqual(body, test_body)

    def test_resolve(self):
        url = URL("http://localhost:8000/tests/index.html")
        header, body = url.request()
        expected_url_css = "http://localhost:8000/tests/index.css"

        self.assertEqual(url.resolve("index.css").url, expected_url_css)
        self.assertEqual(
            url.resolve("../index.css").url, "http://localhost:8000/index.css"
        )
        self.assertEqual(
            url.resolve("//localhost:8000/tests/index.css").url, expected_url_css
        )
        self.assertEqual(url.resolve("/tests/index.css").url, expected_url_css)
