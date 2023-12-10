import unittest
from html_parser import Element, Text, HTMLParser


class TestHTMLParser(unittest.TestCase):
    def test_get_attribute(self):
        test_text = (
            'meta name="viewport" content="width=device-width,initial-scale=1.0" /'
        )
        tag, attribute = HTMLParser(body=None).get_attribute(test_text)

        self.assertEqual(tag, "meta")
        self.assertEqual(attribute["name"], "viewport")
        self.assertEqual(attribute["content"],
                         "width=device-width,initial-scale=1.0")
        self.assertEqual(attribute["/"], "")

    def test_parse(self):
        with open("./tests/index.html") as file:
            test_body = file.read()
        elements = HTMLParser(body=test_body).parse()

        # html lang="en"
        element_html = elements
        self.assertIsInstance(element_html, Element)
        self.assertEqual(element_html.tag, "html")
        self.assertEqual(element_html.attribute["lang"], "en")

        # head
        element_head = element_html.children[0]
        self.assertIsInstance(element_head, Element)
        self.assertEqual(element_head.tag, "head")

        element_head_children = element_head.children

        # meta charset="UTF-8" /
        element_meta = element_head_children[0]
        self.assertIsInstance(element_meta, Element)
        self.assertEqual(element_meta.tag, "meta")
        self.assertEqual(element_meta.attribute["charset"], "UTF-8")
        self.assertEqual(element_meta.attribute["/"], "")

        # meta http-equiv="X-UA-Compatible" content="IE=edge" /
        element_meta = element_head_children[1]
        self.assertIsInstance(element_meta, Element)
        self.assertEqual(element_meta.tag, "meta")
        self.assertEqual(
            element_meta.attribute["http-equiv"], "X-UA-Compatible")
        self.assertEqual(element_meta.attribute["content"], "IE=edge")
        self.assertEqual(element_meta.attribute["/"], "")

        # meta name="viewport" content="width=device-width, initial-scale=1.0" /
        element_meta = element_head_children[2]
        self.assertIsInstance(element_meta, Element)
        self.assertEqual(element_meta.tag, "meta")
        self.assertEqual(element_meta.attribute["name"], "viewport")
        self.assertEqual(
            element_meta.attribute["content"], "width=device-width,initial-scale=1.0"
        )
        self.assertEqual(element_meta.attribute["/"], "")

        # FIXME title 要素をウィンドウのタイトルに据える
        # title
        element_title = element_head_children[3]
        self.assertIsInstance(element_title, Element)
        self.assertEqual(element_title.tag, 'title')
        
        text_title = element_title.children[0]
        self.assertIsInstance(text_title, Text)
        self.assertEqual(text_title.text, 'This is title')

        # # Document
        # text_document = element_title.children[0]
        # self.assertIsInstance(text_document, Text)
        # self.assertEqual(text_document.text, 'Document')

        # body
        element_body = element_html.children[1]
        self.assertIsInstance(element_body, Element)
        self.assertEqual(element_body.tag, "body")

        # Normal
        text_normal = element_body.children[0]
        self.assertIsInstance(text_normal, Text)
        self.assertEqual(text_normal.text, "Normal")

        # i
        element_i = element_body.children[1]
        self.assertIsInstance(element_i, Element)
        self.assertEqual(element_i.tag, "i")

        # Italic
        text_Italic = element_i.children[0]
        self.assertIsInstance(text_Italic, Text)
        self.assertEqual(text_Italic.text, "Italic")

        # b
        element_b = element_body.children[2]
        self.assertIsInstance(element_b, Element)
        self.assertEqual(element_b.tag, "b")

        # Bold
        text_Bold = element_b.children[0]
        self.assertIsInstance(text_Bold, Text)
        self.assertEqual(text_Bold.text, "Bold")

        # small
        element_small = element_body.children[3]
        self.assertIsInstance(element_small, Element)
        self.assertEqual(element_small.tag, "small")

        # Small
        text_Small = element_small.children[0]
        self.assertIsInstance(text_Small, Text)
        self.assertEqual(text_Small.text, "Small")

        # big
        element_big = element_body.children[4]
        self.assertIsInstance(element_big, Element)
        self.assertEqual(element_big.tag, "big")

        # Big
        text_Big = element_big.children[0]
        self.assertIsInstance(text_Big, Text)
        self.assertEqual(text_Big.text, "Big")

        # br
        element_br = element_body.children[5]
        self.assertIsInstance(element_br, Element)
        self.assertEqual(element_br.tag, "br")

        # Newline
        text_newline = element_body.children[6]
        self.assertIsInstance(text_newline, Text)
        self.assertEqual(text_newline.text, "Newline")

        # br/
        element_br = element_body.children[7]
        self.assertIsInstance(element_br, Element)
        self.assertEqual(element_br.tag, "br/")

        # Newline
        text_newline = element_body.children[8]
        self.assertIsInstance(text_newline, Text)
        self.assertEqual(text_newline.text, "Newline")

        # br /
        element_br = element_body.children[9]
        self.assertIsInstance(element_br, Element)
        self.assertEqual(element_br.tag, "br")

        # Newline
        text_newline = element_body.children[10]
        self.assertIsInstance(text_newline, Text)
        self.assertEqual(text_newline.text, "Newline")

        # p
        element_p = element_body.children[11]
        self.assertIsInstance(element_p, Element)
        self.assertEqual(element_p.tag, "p")

        # Paragraph
        text_Paragraph = element_p.children[0]
        self.assertIsInstance(text_Paragraph, Text)
        self.assertEqual(text_Paragraph.text, "Paragraph")

        # Normal
        text_normal = element_body.children[12]
        self.assertIsInstance(text_normal, Text)
        self.assertEqual(text_normal.text, "Normal")

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
        self.assertEqual(text_normal.text, "Normal")
