import unittest
from test.support import captured_stdout
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
from browser import *
from html_parser import *
from url import *
from layout import *

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
        
    def test_load(self):
        test_url = "http://localhost:8000/tests/index.html"
        Browser().load(test_url)

    def test_magnify(self):
        test_url = "http://localhost:8000/tests/index.html"
        browser = Browser()
        browser.load(test_url)
        for _ in range(100):
            browser.magnify(None)
            # TODO フォントサイズについて assertion を追加する

    def test_reduce(self):
        test_url = "http://localhost:8000/tests/index.html"
        browser = Browser()
        # TODO フォントサイズについて assertion を追加する
        browser.load(test_url)
        browser.magnify(None)
        browser.magnify(None)
        browser.magnify(None)
        browser.reduce(None)
        browser.reduce(None)
        browser.reduce(None)
        browser.reduce(None)
        
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

class TestHTMLParser(unittest.TestCase):
    def test_get_attribute(self):
        test_text = 'meta name="viewport" content="width=device-width,initial-scale=1.0" /'
        tag, attribute = HTMLParser(body=None).get_attribute(test_text)

        self.assertEqual(tag, "meta")
        self.assertEqual(attribute["name"], "viewport")
        self.assertEqual(attribute["content"], "width=device-width,initial-scale=1.0")
        self.assertEqual(attribute["/"], "")
        
    def test_parse(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        elements = HTMLParser(body=test_body).parse()
        
        # html lang="en"
        element_html = elements
        self.assertIsInstance(element_html, Element)
        self.assertEqual(element_html.tag, 'html')
        self.assertEqual(element_html.attribute["lang"], 'en')
        
        # head
        element_head = element_html.children[0]
        self.assertIsInstance(element_head, Element)
        self.assertEqual(element_head.tag, 'head')
        
        element_head_children = element_head.children
        
        # meta charset="UTF-8" /
        element_meta = element_head_children[0]
        self.assertIsInstance(element_meta, Element)
        self.assertEqual(element_meta.tag, 'meta')
        self.assertEqual(element_meta.attribute["charset"], 'UTF-8')
        self.assertEqual(element_meta.attribute["/"], '')
        
        # meta http-equiv="X-UA-Compatible" content="IE=edge" /
        element_meta = element_head_children[1]
        self.assertIsInstance(element_meta, Element)
        self.assertEqual(element_meta.tag, 'meta')
        self.assertEqual(element_meta.attribute["http-equiv"], 'X-UA-Compatible')
        self.assertEqual(element_meta.attribute["content"], 'IE=edge')
        self.assertEqual(element_meta.attribute["/"], '')
        
        # meta name="viewport" content="width=device-width, initial-scale=1.0" /
        element_meta = element_head_children[2]
        self.assertIsInstance(element_meta, Element)
        self.assertEqual(element_meta.tag, 'meta')
        self.assertEqual(element_meta.attribute["name"], 'viewport')
        self.assertEqual(element_meta.attribute["content"], 'width=device-width,initial-scale=1.0')
        self.assertEqual(element_meta.attribute["/"], '')
        
        # TODO title 要素をウィンドウのタイトルに据える
        # # title
        # element_title = element_head_children[3]
        # self.assertIsInstance(element_title, Element)
        # self.assertEqual(element_title.tag, 'title')
        
        # # Document
        # text_document = element_title.children[0]
        # self.assertIsInstance(text_document, Text)
        # self.assertEqual(text_document.text, 'Document')
        
        # body
        element_body = element_html.children[1]
        self.assertIsInstance(element_body, Element)
        self.assertEqual(element_body.tag, 'body')
        
        # Normal
        text_normal = element_body.children[0]
        self.assertIsInstance(text_normal, Text)
        self.assertEqual(text_normal.text, 'Normal')
        
        # i
        element_i = element_body.children[1]
        self.assertIsInstance(element_i, Element)
        self.assertEqual(element_i.tag, 'i')

        # Italic
        text_Italic = element_i.children[0]
        self.assertIsInstance(text_Italic, Text)
        self.assertEqual(text_Italic.text, 'Italic')
        
        # b
        element_b = element_body.children[2]
        self.assertIsInstance(element_b, Element)
        self.assertEqual(element_b.tag, 'b')

        # Bold
        text_Bold = element_b.children[0]
        self.assertIsInstance(text_Bold, Text)
        self.assertEqual(text_Bold.text, 'Bold')
        
        # small
        element_small = element_body.children[3]
        self.assertIsInstance(element_small, Element)
        self.assertEqual(element_small.tag, 'small')

        # Small
        text_Small = element_small.children[0]
        self.assertIsInstance(text_Small, Text)
        self.assertEqual(text_Small.text, 'Small')
        
        # big
        element_big = element_body.children[4]
        self.assertIsInstance(element_big, Element)
        self.assertEqual(element_big.tag, 'big')

        # Big
        text_Big = element_big.children[0]
        self.assertIsInstance(text_Big, Text)
        self.assertEqual(text_Big.text, 'Big')
        
        # br
        element_br = element_body.children[5]
        self.assertIsInstance(element_br, Element)
        self.assertEqual(element_br.tag, 'br')
        
        # Newline
        text_newline = element_body.children[6]
        self.assertIsInstance(text_newline, Text)
        self.assertEqual(text_newline.text, 'Newline')
        
        # br/
        element_br = element_body.children[7]
        self.assertIsInstance(element_br, Element)
        self.assertEqual(element_br.tag, 'br/')
        
        # Newline
        text_newline = element_body.children[8]
        self.assertIsInstance(text_newline, Text)
        self.assertEqual(text_newline.text, 'Newline')
        
        # br /
        element_br = element_body.children[9]
        self.assertIsInstance(element_br, Element)
        self.assertEqual(element_br.tag, 'br')
        
        # Newline
        text_newline = element_body.children[10]
        self.assertIsInstance(text_newline, Text)
        self.assertEqual(text_newline.text, 'Newline')
        
        # p
        element_p = element_body.children[11]
        self.assertIsInstance(element_p, Element)
        self.assertEqual(element_p.tag, 'p')
        
        # Paragraph
        text_Paragraph = element_p.children[0]
        self.assertIsInstance(text_Paragraph, Text)
        self.assertEqual(text_Paragraph.text, 'Paragraph')
        
        # Normal
        text_normal = element_body.children[12]
        self.assertIsInstance(text_normal, Text)
        self.assertEqual(text_normal.text, 'Normal')

        # h1
        element_h = element_body.children[13]
        self.assertIsInstance(element_h, Element)
        self.assertEqual(element_h.tag, "h1")
        
        # Heading 1
        text_heading = element_h.children[0]
        self.assertIsInstance(text_heading, Text)
        self.assertEqual(text_heading.text, "Heading 1")

        # h2
        element_h = element_body.children[14]
        self.assertIsInstance(element_h, Element)
        self.assertEqual(element_h.tag, "h2")
        
        # Heading 2
        text_heading = element_h.children[0]
        self.assertIsInstance(text_heading, Text)
        self.assertEqual(text_heading.text, "Heading 2")
        
        # h3
        element_h = element_body.children[15]
        self.assertIsInstance(element_h, Element)
        self.assertEqual(element_h.tag, "h3")
        
        # Heading
        text_heading = element_h.children[0]
        self.assertIsInstance(text_heading, Text)
        self.assertEqual(text_heading.text, "Heading 3")
        
        # h4
        element_h = element_body.children[16]
        self.assertIsInstance(element_h, Element)
        self.assertEqual(element_h.tag, "h4")
        
        # Heading
        text_heading = element_h.children[0]
        self.assertIsInstance(text_heading, Text)
        self.assertEqual(text_heading.text, "Heading 4")
        
        # h5
        element_h = element_body.children[17]
        self.assertIsInstance(element_h, Element)
        self.assertEqual(element_h.tag, "h5")
        
        # Heading 5
        text_heading = element_h.children[0]
        self.assertIsInstance(text_heading, Text)
        self.assertEqual(text_heading.text, "Heading 5")

        # h6
        element_h = element_body.children[18]
        self.assertIsInstance(element_h, Element)
        self.assertEqual(element_h.tag, "h6")
        
        # Heading 6
        text_heading = element_h.children[0]
        self.assertIsInstance(text_heading, Text)
        self.assertEqual(text_heading.text, "Heading 6")
        
        # Normal
        text_normal = element_body.children[19]
        self.assertIsInstance(text_normal, Text)
        self.assertEqual(text_normal.text, 'Normal')

class TestBlockLayout(unittest.TestCase):
    def test_set_text(self):
        tkinter.Tk()
        block = BlockLayout(None, None, None)
        block.line = []
        block.font_size = 20
        block.font_weight = "bold"
        block.font_style = "italic"
        test_text = "This is a test."
        block.set_text(text_node=Text(text=test_text, parent=None))
        
        for actual_text, expected_text in zip(block.line, test_text.split()):
            self.assertEqual(actual_text[0], expected_text)
            self.assertEqual(actual_text[1].configure()["family"], 'None')
            self.assertEqual(actual_text[1].configure()["size"], 20)
            self.assertEqual(actual_text[1].configure()["weight"], "bold")
            self.assertEqual(actual_text[1].configure()["slant"], "italic")
            self.assertEqual(actual_text[1].configure()["underline"], 0)
            self.assertEqual(actual_text[1].configure()["overstrike"], 0)
            
    def test_set_position(self):
        tkinter.Tk()
        block = BlockLayout(None, None, None)
        block.line = []
        block.cursor_x = 0
        block.cursor_y = 0
        block.baseline = 0
        
        block.font_size = 20
        block.font_weight = "bold"
        test_text_1 = "An"
        block.set_text(text_node=Text(text=test_text_1, parent=None))
        
        block.font_size = 15
        block.font_weight = "bold"
        test_text_2 = "apple."
        block.set_text(text_node=Text(text=test_text_2, parent=None))
        
        display_list = block.set_position()
        
        
        expected_list = []
        expected_list.append((0, 0, test_text_1))
        expected_list.append((31, 5, test_text_2))
        
        for actual, expected in zip(display_list, expected_list):
            actual_x, actual_y, actual_text, _ = actual
            expected_x, expected_y, expected_text = expected
            
            self.assertEqual(actual_x, expected_x)
            self.assertEqual(actual_y, expected_y)
            self.assertEqual(actual_text, expected_text)

class TestDocumentLayout(unittest.TestCase):
    def test_layout(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        tkinter.Tk()
        dom = HTMLParser(body=test_body).parse()
        document = DocumentLayout(dom, width=400, height=800)
        display_list = document.layout()

        # 期待される値
        expected = [
            {'x': 0,   'y': 21,      'text': 'Normal',    'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 58,  'y': 19.75,   'text': 'Italic',    'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'italic'}, 
            {'x': 97,  'y': 21,      'text': 'Bold',      'font_family': 'None', 'font_size': 16, 'font_weight': 'bold',   'font_style': 'roman' }, 
            {'x': 136, 'y': 22.25,   'text': 'Small',     'font_family': 'None', 'font_size': 14, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 176, 'y': 16,      'text': 'Big',       'font_family': 'None', 'font_size': 20, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 0,   'y': 39.75,   'text': 'Newline',   'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'roman' },
            {'x': 0,   'y': 58.5,    'text': 'Newline',   'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 0,   'y': 77.25,   'text': 'Newline',   'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 0,   'y': 112,     'text': 'Paragraph', 'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 0,   'y': 146.75,  'text': 'Normal',    'font_family': 'None', 'font_size': 16, 'font_weight': 'normal', 'font_style': 'roman' }, 
            {'x': 0,   'y': 165.5,   'text': 'Heading',   'font_family': 'None', 'font_size': 48, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 197, 'y': 165.5,   'text': '1',         'font_family': 'None', 'font_size': 48, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 0,   'y': 239,     'text': 'Heading',   'font_family': 'None', 'font_size': 32, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 133, 'y': 239,     'text': '2',         'font_family': 'None', 'font_size': 32, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 0,   'y': 293.75,  'text': 'Heading',   'font_family': 'None', 'font_size': 24, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 101,  'y': 293.75,  'text': '3',         'font_family': 'None', 'font_size': 24, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 0,   'y': 338.5,   'text': 'Heading',   'font_family': 'None', 'font_size': 17, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 73,  'y': 338.5,   'text': '4',         'font_family': 'None', 'font_size': 17, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 0,   'y': 374.5,   'text': 'Heading',   'font_family': 'None', 'font_size': 12, 'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 55,  'y': 374.5,   'text': '5',         'font_family': 'None', 'font_size': 12, 'font_weight': 'bold', 'font_style': 'roman' },
            {'x': 0,   'y': 405.5,   'text': 'Heading',   'font_family': 'None', 'font_size': 8,  'font_weight': 'bold', 'font_style': 'roman' }, 
            {'x': 38,  'y': 405.5,   'text': '6',         'font_family': 'None', 'font_size': 8,  'font_weight': 'bold', 'font_style': 'roman' }
        ]
        
        for i, exp in enumerate(expected):        
            self.assertEqual(display_list[i][0], exp["x"]+document.HSTEP)
            self.assertEqual(display_list[i][1], exp["y"])
            self.assertEqual(display_list[i][2], exp["text"])
            self.assertEqual(display_list[i][3].configure()["family"], exp["font_family"])
            self.assertEqual(display_list[i][3].configure()["size"], exp["font_size"])
            self.assertEqual(display_list[i][3].configure()["weight"], exp["font_weight"])
            self.assertEqual(display_list[i][3].configure()["slant"], exp["font_style"])