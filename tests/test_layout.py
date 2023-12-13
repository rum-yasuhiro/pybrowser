import unittest
import tkinter
from browser import layout_tree
from html_parser import Text, HTMLParser
from layout import DocumentLayout, BlockLayout, DrawRect

class TestDocumentLayout(unittest.TestCase):
    def test_layout(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        tkinter.Tk()
        dom_node = HTMLParser(body=test_body).parse()
        test_width = 400
        document = DocumentLayout(dom_node, width=test_width)
        document.layout()
        display_list = []
        layout_tree(document, display_list)

        # 期待される値
        expected = [
            {
                "left": 0,
                "top": 21,
                "text": "Normal",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 58,
                "top": 19.75,
                "text": "Italic",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "italic",
            },
            {
                "left": 97,
                "top": 21,
                "text": "Bold",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 136,
                "top": 22.25,
                "text": "Small",
                "font_family": "None",
                "font_size": 14,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 176,
                "top": 16,
                "text": "Big",
                "font_family": "None",
                "font_size": 20,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 46.0,
                "text": "Newline",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 69.75,
                "text": "Newline",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 93.5,
                "text": "Newline",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 133.25,
                "text": "Paragraph",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 173,
                "text": "Normal",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 208.75,
                "text": "Heading",
                "font_family": "None",
                "font_size": 48,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 197,
                "top": 208.75,
                "text": "1",
                "font_family": "None",
                "font_size": 48,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 312,
                "text": "Heading",
                "font_family": "None",
                "font_size": 32,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 133,
                "top": 312,
                "text": "2",
                "font_family": "None",
                "font_size": 32,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 381.5,
                "text": "Heading",
                "font_family": "None",
                "font_size": 24,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 101,
                "top": 381.5,
                "text": "3",
                "font_family": "None",
                "font_size": 24,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 434,
                "text": "Heading",
                "font_family": "None",
                "font_size": 17,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 73,
                "top": 434,
                "text": "4",
                "font_family": "None",
                "font_size": 17,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 470.5,
                "text": "Heading",
                "font_family": "None",
                "font_size": 12,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 55,
                "top": 470.5,
                "text": "5",
                "font_family": "None",
                "font_size": 12,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 497.25,
                "text": "Heading",
                "font_family": "None",
                "font_size": 8,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 38,
                "top": 497.25,
                "text": "6",
                "font_family": "None",
                "font_size": 8,
                "font_weight": "bold",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 513.75,
                "text": "Normal",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 537.5,
                "right": test_width - 2*document.HSTEP,
                "bottom": 561.25,
                "color": "gray"
            },
            {
                "left": 0,
                "top": 537.5,
                "text": "$",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 15,
                "top": 537.5,
                "text": "python",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 71,
                "top": 537.5,
                "text": "hello_world.py",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 561.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 13,
                "top": 561.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 585,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 13,
                "top": 585,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 32,
                "top": 608.75,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 45,
                "top": 608.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 32,
                "top": 632.5,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 45,
                "top": 632.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 64,
                "top": 656.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 77,
                "top": 656.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 64,
                "top": 680.0,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 77,
                "top": 680.0,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 96,
                "top": 703.75,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 109,
                "top": 703.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 96,
                "top": 727.5,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 109,
                "top": 727.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 64,
                "top": 751.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 77,
                "top": 751.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 64,
                "top": 775,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 77,
                "top": 775,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 32,
                "top": 798.75,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 45,
                "top": 798.75,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 32,
                "top": 822.5,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 45,
                "top": 822.5,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 846.25,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 13,
                "top": 846.25,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 0,
                "top": 870,
                "text": "•",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
            {
                "left": 13,
                "top": 870,
                "text": "item",
                "font_family": "None",
                "font_size": 16,
                "font_weight": "normal",
                "font_style": "roman",
            },
        ]
        
        for i, exp in enumerate(expected):
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
            self.assertEqual(actual_text[1], expected_text)
            self.assertEqual(actual_text[2].configure()["family"], "None")
            self.assertEqual(actual_text[2].configure()["size"], 20)
            self.assertEqual(actual_text[2].configure()["weight"], "bold")
            self.assertEqual(actual_text[2].configure()["slant"], "italic")
            self.assertEqual(actual_text[2].configure()["underline"], 0)
            self.assertEqual(actual_text[2].configure()["overstrike"], 0)

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

        block.set_position()

        expected_list = []
        expected_list.append((0, 0, test_text_1))
        expected_list.append((31, 5, test_text_2))

        for actual, expected in zip(block.display_list, expected_list):
            actual_x, actual_y, actual_text, _ = actual
            expected_x, expected_y, expected_text = expected

            self.assertEqual(actual_x, expected_x)
            self.assertEqual(actual_y, expected_y)
            self.assertEqual(actual_text, expected_text)

