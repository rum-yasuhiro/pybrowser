import unittest
import tkinter
from tkinter.font import Font
from browser import layout_tree
from html_parser import Text, Element, HTMLParser
from css_parser import style
from layout import DocumentLayout, BlockLayout, DrawRect, DrawText

class TestBlockLayout(unittest.TestCase):
    def setUp(self):
        self.dom_node = Element(None, None, None)
        self.block = BlockLayout(self.dom_node, None, None)
    
    def test_paint_1(self):
        self.dom_node.tag = "pre"
        self.block.height = 0
        cmds = self.block.paint()
        
        self.assertIsInstance(cmds[0], DrawRect)
        self.assertEqual(cmds[0].color, "gray")

    def test_paint_2(self):
        self.dom_node.style = {"background-color": "red"}
        self.block.height = 0
        cmds = self.block.paint()
        
        self.assertIsInstance(cmds[0], DrawRect)
        self.assertEqual(cmds[0].color, "red")
    
    def test_paint_3(self):
        dom_node = Text(None, None)
        block = BlockLayout(dom_node, None, None)
        tkinter.Tk()
        block.display_list = [(0, 0, "test", Font())]
        cmds = block.paint()
        
        self.assertIsInstance(cmds[0], DrawText)
        self.assertEqual(cmds[0].left, 0)
        self.assertEqual(cmds[0].top, 0)
        self.assertEqual(cmds[0].text, "test")
        self.assertIsInstance(cmds[0].font, Font)
    
    def test_layout_mode_1(self):
        child_dom_node = Element(
            tag="body",
            attribute=None,
            parent=None
        )
        self.dom_node.children = [child_dom_node]      
        
        mode = self.block.layout_mode()
        self.assertEqual(mode, "block")
    
    def test_layout_mode_2(self):
        child_dom_node = Element(
            tag="br",
            attribute=None,
            parent=None
        )
        self.dom_node.children = [child_dom_node]
        
        mode =self.block.layout_mode()
        self.assertEqual(mode, "inline")
    
    def test_layout_mode_3(self):
        dom_node = Text(text=None, parent=None)
        block = BlockLayout(dom_node, None, None)
        
        mode = block.layout_mode()
        self.assertEqual(mode, "inline")
    
    def test_layout_mode(self):
        child_dom_node = Element(
            tag="body",
            attribute=None,
            parent=None
        )
        self.dom_node.children = [
            child_dom_node
        ]
        
        mode = self.block.layout_mode()
        self.assertEqual(mode, "block")
    
    def test_recurse_1(self):
        self.block.line = []
        dom_node = Text("This is a test.", None)
        tkinter.Tk()
        self.block.recurse(dom_node)
        
        self.assertEqual(self.block.line[0][0], 0)
        self.assertEqual(self.block.line[0][1], "This")
        self.assertEqual(self.block.line[1][0], 36)
        self.assertEqual(self.block.line[1][1], "is")
        self.assertEqual(self.block.line[2][0], 53)
        self.assertEqual(self.block.line[2][1], "a")
        self.assertEqual(self.block.line[3][0], 67)
        self.assertEqual(self.block.line[3][1], "test.")
    
    def test_recurse_2(self):
        self.block.line = []
        
        child_node = Text("This is a test.", None)
        self.dom_node.tag = "b"
        self.dom_node.children.append(child_node)
        
        tkinter.Tk()
        self.block.recurse(self.dom_node)
        
        self.assertEqual(self.block.line[0][0], 0)
        self.assertEqual(self.block.line[0][1], "This")
        self.assertEqual(self.block.line[1][0], 38)
        self.assertEqual(self.block.line[1][1], "is")
        self.assertEqual(self.block.line[2][0], 56)
        self.assertEqual(self.block.line[2][1], "a")
        self.assertEqual(self.block.line[3][0], 70)
        self.assertEqual(self.block.line[3][1], "test.")
        
    def test_recurse_3(self):
        self.block.line = []
        
        child_node = Text("This is a test.", None)
        self.dom_node.tag = "h1"
        self.dom_node.children.append(child_node)
        
        tkinter.Tk()
        self.block.recurse(self.dom_node)
        
        self.assertEqual(self.block.line, [])
        
    def test_set_text(self):
        tkinter.Tk()
        self.block.line = []
        self.block.font_size = 20
        self.block.font_weight = "bold"
        self.block.font_style = "italic"
        test_text = "This is a test."
        self.block.set_text(text_node=Text(text=test_text, parent=None))

        for actual_text, expected_text in zip(self.block.line, test_text.split()):
            self.assertEqual(actual_text[1], expected_text)
            self.assertEqual(actual_text[2].configure()["family"], "None")
            self.assertEqual(actual_text[2].configure()["size"], 20)
            self.assertEqual(actual_text[2].configure()["weight"], "bold")
            self.assertEqual(actual_text[2].configure()["slant"], "italic")
            self.assertEqual(actual_text[2].configure()["underline"], 0)
            self.assertEqual(actual_text[2].configure()["overstrike"], 0)

    def test_get_font(self):    
        tkinter.Tk()
        expected_1 = (None, 10, "normal", "roman")
        font_1 = self.block.get_font(*expected_1)
        self.assertIsInstance(font_1, Font)
        font_2 = self.block.get_font(*expected_1)
        self.assertEqual(font_1, font_2)
        
        expected_2 = (None, 15, "bold", "italic")
        font_3 = self.block.get_font(*expected_2)
        self.assertIsInstance(font_3, Font)
        self.assertNotEqual(font_3, font_1)
        font_4 = self.block.get_font(*expected_2)
        self.assertEqual(font_3, font_4)
        
    def test_set_position(self):
        tkinter.Tk()
        self.block.line = []
        self.block.cursor_x = 0
        self.block.cursor_y = 0
        self.block.baseline = 0

        self.block.font_size = 20
        self.block.font_weight = "bold"
        test_text_1 = "An"
        self.block.set_text(text_node=Text(text=test_text_1, parent=None))

        self.block.font_size = 15
        self.block.font_weight = "bold"
        test_text_2 = "apple."
        self.block.set_text(text_node=Text(text=test_text_2, parent=None))

        self.block.set_position()

        expected_list = []
        expected_list.append((0, 0, test_text_1))
        expected_list.append((31, 5, test_text_2))

        for actual, expected in zip(self.block.display_list, expected_list):
            actual_x, actual_y, actual_text, _ = actual
            expected_x, expected_y, expected_text = expected

            self.assertEqual(actual_x, expected_x)
            self.assertEqual(actual_y, expected_y)
            self.assertEqual(actual_text, expected_text)

class TestDocumentLayout(unittest.TestCase):
    def test_paint(self):
        document = DocumentLayout(None)
        display_list = document.paint()
        self.assertEqual(display_list, [])
        
    def test_layout(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        tkinter.Tk()
        dom_node = HTMLParser(body=test_body).parse()
        style(dom_node)
        test_width = 400
        document = DocumentLayout(dom_node, width=test_width)
        document.layout()
        display_list = []
        layout_tree(document, display_list)

        # 期待される値
        expected = [
            {
                "idx": 0,
                "left": 0,
                "top": 21,
                "text": "Normal",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 1,
                "left": 58,
                "top": 19.75,
                "text": "Italic",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "italic",
            },
            {
                "idx": 2,
                "left": 97,
                "top": 21,
                "text": "Bold",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 3,
                "left": 136,
                "top": 22.25,
                "text": "Small",
                "font_family": "None",
                "font_size": 14,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 5,
                "left": 176,
                "top": 16,
                "text": "Big",
                "font_family": "None",
                "font_size": 20,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 6,
                "left": 0,
                "top": 46.0,
                "text": "Newline",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 7,
                "left": 0,
                "top": 69.75,
                "text": "Newline",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 8,
                "left": 0,
                "top": 93.5,
                "text": "Newline",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 9,
                "left": 0,
                "top": 133.25,
                "text": "Paragraph",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 10,
                "left": 0,
                "top": 173,
                "text": "Normal",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 11,
                "left": 0,
                "top": 208.75,
                "text": "Heading",
                "font_family": "None",
                "font_size": 48,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 12,
                "left": 197,
                "top": 208.75,
                "text": "1",
                "font_family": "None",
                "font_size": 48,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 13,
                "left": 0,
                "top": 312,
                "text": "Heading",
                "font_family": "None",
                "font_size": 32,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 14,
                "left": 133,
                "top": 312,
                "text": "2",
                "font_family": "None",
                "font_size": 32,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 15,
                "left": 0,
                "top": 381.5,
                "text": "Heading",
                "font_family": "None",
                "font_size": 24,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 16,
                "left": 101,
                "top": 381.5,
                "text": "3",
                "font_family": "None",
                "font_size": 24,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 17,
                "left": 0,
                "top": 434,
                "text": "Heading",
                "font_family": "None",
                "font_size": 17,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 18,
                "left": 73,
                "top": 434,
                "text": "4",
                "font_family": "None",
                "font_size": 17,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 19,
                "left": 0,
                "top": 470.5,
                "text": "Heading",
                "font_family": "None",
                "font_size": 12,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 20,
                "left": 55,
                "top": 470.5,
                "text": "5",
                "font_family": "None",
                "font_size": 12,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 21,
                "left": 0,
                "top": 497.25,
                "text": "Heading",
                "font_family": "None",
                "font_size": 8,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 22,
                "left": 38,
                "top": 497.25,
                "text": "6",
                "font_family": "None",
                "font_size": 8,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "idx": 23,
                "left": 0,
                "top": 513.75,
                "text": "Normal",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 24,
                "left": 0,
                "top": 537.5,
                "right": test_width - 2*document.HSTEP,
                "bottom": 561.25,
                "color": "gray"
            },
            {
                "idx": 25, 
                "left": 0,
                "top": 537.5,
                "text": "$",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 26,
                "left": 15,
                "top": 537.5,
                "text": "python",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 27,
                "left": 71,
                "top": 537.5,
                "text": "hello_world.py",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 28,
                "left": 0,
                "top": 561.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 29,
                "left": 13,
                "top": 561.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 30,
                "left": 0,
                "top": 585,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 31,
                "left": 13,
                "top": 585,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 32,
                "left": 32,
                "top": 608.75,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 33,
                "left": 45,
                "top": 608.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 34,
                "left": 32,
                "top": 632.5,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 35,
                "left": 45,
                "top": 632.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 36,
                "left": 64,
                "top": 656.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 37,
                "left": 77,
                "top": 656.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 38,
                "left": 64,
                "top": 680.0,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 39,
                "left": 77,
                "top": 680.0,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 40,
                "left": 96,
                "top": 703.75,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 41,
                "left": 109,
                "top": 703.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 42,
                "left": 96,
                "top": 727.5,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 43,
                "left": 109,
                "top": 727.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 44,
                "left": 64,
                "top": 751.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 45,
                "left": 77,
                "top": 751.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 46,
                "left": 64,
                "top": 775,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 47,
                "left": 77,
                "top": 775,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 48,
                "left": 32,
                "top": 798.75,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 49,
                "left": 45,
                "top": 798.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 50,
                "left": 32,
                "top": 822.5,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 51,
                "left": 45,
                "top": 822.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 52,
                "left": 0,
                "top": 846.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 53,
                "left": 13,
                "top": 846.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 54,
                "left": 0,
                "top": 870,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 55,
                "left": 13,
                "top": 870,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 56,
                "left": 32,
                "top": 893.75,
                "text": "1",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 57,
                "left": 45,
                "top": 893.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 58,
                "left": 32,
                "top": 917.5,
                "text": "2",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 59,
                "left": 47,
                "top": 917.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 60,
                "left": 64,
                "top": 941.25,
                "text": "1",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 61,
                "left": 77,
                "top": 941.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 62,
                "left": 64,
                "top": 965,
                "text": "2",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 63,
                "left": 79,
                "top": 965,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 64,
                "left": 96,
                "top": 988.75,
                "text": "1",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 65,
                "left": 109,
                "top": 988.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 66,
                "left": 96,
                "top": 1012.5,
                "text": "2",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 67,
                "left": 111,
                "top": 1012.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 68,
                "left": 64,
                "top": 1036.25,
                "text": "3",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 69,
                "left": 79,
                "top": 1036.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 70,
                "left": 64,
                "top": 1060,
                "text": "4",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 71,
                "left": 79,
                "top": 1060,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 72,
                "left": 32,
                "top": 1083.75,
                "text": "3",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 73,
                "left": 47,
                "top": 1083.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 74,
                "left": 32,
                "top": 1107.5,
                "text": "4",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 75,
                "left": 47,
                "top": 1107.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 76,
                "left": 0,
                "top": 1131.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 77,
                "left": 13,
                "top": 1131.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 78,
                "left": 0,
                "top": 1155,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 79,
                "left": 13,
                "top": 1155,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "idx": 80,
                "left": 0,
                "top": 1178.75,
                "right": test_width - 2*document.HSTEP,
                "bottom": 1202.5,
                "color": "lightblue"
            },
            {
                "idx": 81,
                "left": 0,
                "top": 1178.75,
                "text": "Lightblue",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
        ]
        
        for i, exp in enumerate(expected):
            with self.subTest(exp=exp):                
                self.assertEqual(display_list[i].left, exp["left"] + document.HSTEP)
                self.assertEqual(display_list[i].top, exp["top"])
                if isinstance(display_list[i], DrawRect):
                    self.assertEqual(display_list[i].right, exp["right"] + document.HSTEP)
                    self.assertEqual(display_list[i].bottom, exp["bottom"])
                else:
                    self.assertEqual(display_list[i].text, exp["text"])
                    self.assertEqual(
                        display_list[i].font.configure()["family"], exp["font_family"]
                    )
                    self.assertEqual(
                        display_list[i].font.configure()["size"], exp["font_size"]
                    )
                    self.assertEqual(
                        display_list[i].font.configure()["weight"], exp["font_weight"]
                    )
                    self.assertEqual(
                        display_list[i].font.configure()["slant"], exp["font_style"]
                    )
