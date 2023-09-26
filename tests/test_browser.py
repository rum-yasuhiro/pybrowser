import unittest
from test.support import captured_stdout
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
from browser import *
from url import *
from layout import *


class TestBrowser(unittest.TestCase):
    def test_lex(self):
        test_body = "<body><h1>Test</h1></body>"
        token_list = Browser().lex(body=test_body)
        self.assertEqual(token_list[0].tag, "body")
        self.assertEqual(token_list[1].tag, "h1")
        self.assertEqual(token_list[2].text, "Test")
        self.assertEqual(token_list[3].tag, "/h1")
        self.assertEqual(token_list[4].tag, "/body")

class TestURL(unittest.TestCase):
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

class TestLayout(unittest.TestCase):
    def test_set_text(self):
        tkinter.Tk()
        layout = Layout()
        layout.line = []
        layout.font_size = 20
        layout.font_weight = "bold"
        layout.font_style = "italic"
        test_text = "This is a test."
        layout.set_text(token=Text(text=test_text))
        
        for actual_text, expected_text in zip(layout.line, test_text.split()):
            self.assertEqual(actual_text[0], expected_text)
            self.assertEqual(actual_text[1].configure()["family"], 'None')
            self.assertEqual(actual_text[1].configure()["size"], 20)
            self.assertEqual(actual_text[1].configure()["weight"], "bold")
            self.assertEqual(actual_text[1].configure()["slant"], "italic")
            self.assertEqual(actual_text[1].configure()["underline"], 0)
            self.assertEqual(actual_text[1].configure()["overstrike"], 0)
            
    def test_set_position(self):
        tkinter.Tk()
        layout = Layout()
        layout.line = []
        layout.cursor_x = 0
        layout.cursor_y = 0
        layout.baseline = 0
        
        layout.font_size = 20
        layout.font_weight = "bold"
        test_text_1 = "An"
        layout.set_text(token=Text(text=test_text_1))
        
        layout.font_size = 15
        layout.font_weight = "bold"
        test_text_2 = "apple."
        layout.set_text(token=Text(text=test_text_2))
        
        display_list = layout.set_position()
        
        
        expected_list = []
        expected_list.append((0, 0, test_text_1))
        expected_list.append((31, 5, test_text_2))
        
        for actual, expected in zip(display_list, expected_list):
            actual_x, actual_y, actual_text, _ = actual
            expected_x, expected_y, expected_text = expected
            
            self.assertEqual(actual_x, expected_x)
            self.assertEqual(actual_y, expected_y)
            self.assertEqual(actual_text, expected_text)
    
    def test_arrange(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        token_list = Browser().lex(body=test_body)
        layout = Layout(width=400, height=800)
        layout.HSTEP = 0
        layout.VSTEP = 0
        display_list = layout.arrange(token_list=token_list)
        
        # ノーマル
        self.assertEqual(display_list[0][0], 0)
        self.assertEqual(display_list[0][1], 5)
        self.assertEqual(display_list[0][2], "Normal")
        self.assertEqual(display_list[0][3].configure()["family"], 'None')
        self.assertEqual(display_list[0][3].configure()["size"], 16)
        self.assertEqual(display_list[0][3].configure()["weight"], "normal")
        self.assertEqual(display_list[0][3].configure()["slant"], "roman")
        self.assertEqual(display_list[0][3].configure()["underline"], 0)
        self.assertEqual(display_list[0][3].configure()["overstrike"], 0)
        
        # イタリック体
        self.assertEqual(display_list[1][0], 58)
        self.assertEqual(display_list[1][1], 3.75)
        self.assertEqual(display_list[1][2], "Italic")
        self.assertEqual(display_list[1][3].configure()["family"], 'None')
        self.assertEqual(display_list[1][3].configure()["size"], 16)
        self.assertEqual(display_list[1][3].configure()["weight"], "normal")
        self.assertEqual(display_list[1][3].configure()["slant"], "italic")
        self.assertEqual(display_list[1][3].configure()["underline"], 0)
        self.assertEqual(display_list[1][3].configure()["overstrike"], 0)
        
        # ボールド体
        self.assertEqual(display_list[2][0], 97)
        self.assertEqual(display_list[2][1], 5)
        self.assertEqual(display_list[2][2], "Bold")
        self.assertEqual(display_list[2][3].configure()["family"], 'None')
        self.assertEqual(display_list[2][3].configure()["size"], 16)
        self.assertEqual(display_list[2][3].configure()["weight"], "bold")
        self.assertEqual(display_list[2][3].configure()["slant"], "roman")
        self.assertEqual(display_list[2][3].configure()["underline"], 0)
        self.assertEqual(display_list[2][3].configure()["overstrike"], 0)
        
        # small タグ
        self.assertEqual(display_list[3][0], 136)
        self.assertEqual(display_list[3][1], 6.25)
        self.assertEqual(display_list[3][2], "Small")
        self.assertEqual(display_list[3][3].configure()["family"], 'None')
        self.assertEqual(display_list[3][3].configure()["size"], 14)
        self.assertEqual(display_list[3][3].configure()["weight"], "normal")
        self.assertEqual(display_list[3][3].configure()["slant"], "roman")
        self.assertEqual(display_list[3][3].configure()["underline"], 0)
        self.assertEqual(display_list[3][3].configure()["overstrike"], 0)
        
        # big タグ
        self.assertEqual(display_list[4][0], 176)
        self.assertEqual(display_list[4][1], 0)
        self.assertEqual(display_list[4][2], "Big")
        self.assertEqual(display_list[4][3].configure()["family"], 'None')
        self.assertEqual(display_list[4][3].configure()["size"], 20)
        self.assertEqual(display_list[4][3].configure()["weight"], "normal")
        self.assertEqual(display_list[4][3].configure()["slant"], "roman")
        self.assertEqual(display_list[4][3].configure()["underline"], 0)
        self.assertEqual(display_list[4][3].configure()["overstrike"], 0)
        
        # br タグ
        self.assertEqual(display_list[5][0], 0)
        self.assertEqual(display_list[5][1], 23.75)
        self.assertEqual(display_list[5][2], "Newline")
        self.assertEqual(display_list[5][3].configure()["family"], 'None')
        self.assertEqual(display_list[5][3].configure()["size"], 16)
        self.assertEqual(display_list[5][3].configure()["weight"], "normal")
        self.assertEqual(display_list[5][3].configure()["slant"], "roman")
        self.assertEqual(display_list[5][3].configure()["underline"], 0)
        self.assertEqual(display_list[5][3].configure()["overstrike"], 0)
        
        # br/ タグ
        self.assertEqual(display_list[6][0], 0)
        self.assertEqual(display_list[6][1], 42.5)
        self.assertEqual(display_list[6][2], "Newline")
        self.assertEqual(display_list[6][3].configure()["family"], 'None')
        self.assertEqual(display_list[6][3].configure()["size"], 16)
        self.assertEqual(display_list[6][3].configure()["weight"], "normal")
        self.assertEqual(display_list[6][3].configure()["slant"], "roman")
        self.assertEqual(display_list[6][3].configure()["underline"], 0)
        self.assertEqual(display_list[6][3].configure()["overstrike"], 0)
        
        # br / タグ
        self.assertEqual(display_list[7][0], 0)
        self.assertEqual(display_list[7][1], 61.25)
        self.assertEqual(display_list[7][2], "Newline")
        self.assertEqual(display_list[7][3].configure()["family"], 'None')
        self.assertEqual(display_list[7][3].configure()["size"], 16)
        self.assertEqual(display_list[7][3].configure()["weight"], "normal")
        self.assertEqual(display_list[7][3].configure()["slant"], "roman")
        self.assertEqual(display_list[7][3].configure()["underline"], 0)
        self.assertEqual(display_list[7][3].configure()["overstrike"], 0)
        
        # p タグ
        self.assertEqual(display_list[8][0], 0)
        self.assertEqual(display_list[8][1], 80)
        self.assertEqual(display_list[8][2], "Paragraph")
        self.assertEqual(display_list[8][3].configure()["family"], 'None')
        self.assertEqual(display_list[8][3].configure()["size"], 16)
        self.assertEqual(display_list[8][3].configure()["weight"], "normal")
        self.assertEqual(display_list[8][3].configure()["slant"], "roman")
        self.assertEqual(display_list[8][3].configure()["underline"], 0)
        self.assertEqual(display_list[8][3].configure()["overstrike"], 0)
        
        # /p タグ
        self.assertEqual(display_list[9][0], 0)
        self.assertEqual(display_list[9][1], 98.75)
        self.assertEqual(display_list[9][2], "Normal")
        self.assertEqual(display_list[9][3].configure()["family"], 'None')
        self.assertEqual(display_list[9][3].configure()["size"], 16)
        self.assertEqual(display_list[9][3].configure()["weight"], "normal")
        self.assertEqual(display_list[9][3].configure()["slant"], "roman")
        self.assertEqual(display_list[9][3].configure()["underline"], 0)
        self.assertEqual(display_list[9][3].configure()["overstrike"], 0)
        
        # h1 タグ
        self.assertEqual(display_list[10][0], 0)
        self.assertEqual(display_list[10][1], 117.5)
        self.assertEqual(display_list[10][2], "Heading")
        self.assertEqual(display_list[10][3].configure()["family"], 'None')
        self.assertEqual(display_list[10][3].configure()["size"], 48)
        self.assertEqual(display_list[10][3].configure()["weight"], "normal")
        self.assertEqual(display_list[10][3].configure()["slant"], "roman")
        self.assertEqual(display_list[10][3].configure()["underline"], 0)
        self.assertEqual(display_list[10][3].configure()["overstrike"], 0)
        
        self.assertEqual(display_list[11][0], 184)
        self.assertEqual(display_list[11][1], 117.5)
        self.assertEqual(display_list[11][2], "1")
        self.assertEqual(display_list[11][3].configure()["family"], 'None')
        self.assertEqual(display_list[11][3].configure()["size"], 48)
        self.assertEqual(display_list[11][3].configure()["weight"], "normal")
        self.assertEqual(display_list[11][3].configure()["slant"], "roman")
        self.assertEqual(display_list[11][3].configure()["underline"], 0)
        self.assertEqual(display_list[11][3].configure()["overstrike"], 0)
        
        # h2 タグ
        self.assertEqual(display_list[12][0], 0)
        self.assertEqual(display_list[12][1], 175)
        self.assertEqual(display_list[12][2], "Heading")
        self.assertEqual(display_list[12][3].configure()["family"], 'None')
        self.assertEqual(display_list[12][3].configure()["size"], 32)
        self.assertEqual(display_list[12][3].configure()["weight"], "normal")
        self.assertEqual(display_list[12][3].configure()["slant"], "roman")
        self.assertEqual(display_list[12][3].configure()["underline"], 0)
        self.assertEqual(display_list[12][3].configure()["overstrike"], 0)
    
        self.assertEqual(display_list[13][0], 124)
        self.assertEqual(display_list[13][1], 175)
        self.assertEqual(display_list[13][2], "2")
        self.assertEqual(display_list[13][3].configure()["family"], 'None')
        self.assertEqual(display_list[13][3].configure()["size"], 32)
        self.assertEqual(display_list[13][3].configure()["weight"], "normal")
        self.assertEqual(display_list[13][3].configure()["slant"], "roman")
        self.assertEqual(display_list[13][3].configure()["underline"], 0)
        self.assertEqual(display_list[13][3].configure()["overstrike"], 0)
        
        # h3 タグ
        self.assertEqual(display_list[14][0], 0)
        self.assertEqual(display_list[14][1], 213.75)
        self.assertEqual(display_list[14][2], "Heading")
        self.assertEqual(display_list[14][3].configure()["family"], 'None')
        self.assertEqual(display_list[14][3].configure()["size"], 24)
        self.assertEqual(display_list[14][3].configure()["weight"], "normal")
        self.assertEqual(display_list[14][3].configure()["slant"], "roman")
        self.assertEqual(display_list[14][3].configure()["underline"], 0)
        self.assertEqual(display_list[14][3].configure()["overstrike"], 0)
    
        self.assertEqual(display_list[15][0], 94)
        self.assertEqual(display_list[15][1], 213.75)
        self.assertEqual(display_list[15][2], "3")
        self.assertEqual(display_list[15][3].configure()["family"], 'None')
        self.assertEqual(display_list[15][3].configure()["size"], 24)
        self.assertEqual(display_list[15][3].configure()["weight"], "normal")
        self.assertEqual(display_list[15][3].configure()["slant"], "roman")
        self.assertEqual(display_list[15][3].configure()["underline"], 0)
        self.assertEqual(display_list[15][3].configure()["overstrike"], 0)
        
        # h4 タグ
        self.assertEqual(display_list[16][0], 0)
        self.assertEqual(display_list[16][1], 242.5)
        self.assertEqual(display_list[16][2], "Heading")
        self.assertEqual(display_list[16][3].configure()["family"], 'None')
        self.assertEqual(display_list[16][3].configure()["size"], 17)
        self.assertEqual(display_list[16][3].configure()["weight"], "normal")
        self.assertEqual(display_list[16][3].configure()["slant"], "roman")
        self.assertEqual(display_list[16][3].configure()["underline"], 0)
        self.assertEqual(display_list[16][3].configure()["overstrike"], 0)
    
        self.assertEqual(display_list[17][0], 69)
        self.assertEqual(display_list[17][1], 242.5)
        self.assertEqual(display_list[17][2], "4")
        self.assertEqual(display_list[17][3].configure()["family"], 'None')
        self.assertEqual(display_list[17][3].configure()["size"], 17)
        self.assertEqual(display_list[17][3].configure()["weight"], "normal")
        self.assertEqual(display_list[17][3].configure()["slant"], "roman")
        self.assertEqual(display_list[17][3].configure()["underline"], 0)
        self.assertEqual(display_list[17][3].configure()["overstrike"], 0)
        
        # h5 タグ
        self.assertEqual(display_list[18][0], 0)
        self.assertEqual(display_list[18][1], 262.5)
        self.assertEqual(display_list[18][2], "Heading")
        self.assertEqual(display_list[18][3].configure()["family"], 'None')
        self.assertEqual(display_list[18][3].configure()["size"], 12)
        self.assertEqual(display_list[18][3].configure()["weight"], "normal")
        self.assertEqual(display_list[18][3].configure()["slant"], "roman")
        self.assertEqual(display_list[18][3].configure()["underline"], 0)
        self.assertEqual(display_list[18][3].configure()["overstrike"], 0)
    
        self.assertEqual(display_list[19][0], 52)
        self.assertEqual(display_list[19][1], 262.5)
        self.assertEqual(display_list[19][2], "5")
        self.assertEqual(display_list[19][3].configure()["family"], 'None')
        self.assertEqual(display_list[19][3].configure()["size"], 12)
        self.assertEqual(display_list[19][3].configure()["weight"], "normal")
        self.assertEqual(display_list[19][3].configure()["slant"], "roman")
        self.assertEqual(display_list[19][3].configure()["underline"], 0)
        self.assertEqual(display_list[19][3].configure()["overstrike"], 0)
        
        # h6 タグ
        self.assertEqual(display_list[20][0], 0)
        self.assertEqual(display_list[20][1], 277.5)
        self.assertEqual(display_list[20][2], "Heading")
        self.assertEqual(display_list[20][3].configure()["family"], 'None')
        self.assertEqual(display_list[20][3].configure()["size"], 8)
        self.assertEqual(display_list[20][3].configure()["weight"], "normal")
        self.assertEqual(display_list[20][3].configure()["slant"], "roman")
        self.assertEqual(display_list[20][3].configure()["underline"], 0)
        self.assertEqual(display_list[20][3].configure()["overstrike"], 0)
    
        self.assertEqual(display_list[21][0], 36)
        self.assertEqual(display_list[21][1], 277.5)
        self.assertEqual(display_list[21][2], "6")
        self.assertEqual(display_list[21][3].configure()["family"], 'None')
        self.assertEqual(display_list[21][3].configure()["size"], 8)
        self.assertEqual(display_list[21][3].configure()["weight"], "normal")
        self.assertEqual(display_list[21][3].configure()["slant"], "roman")
        self.assertEqual(display_list[21][3].configure()["underline"], 0)
        self.assertEqual(display_list[21][3].configure()["overstrike"], 0)