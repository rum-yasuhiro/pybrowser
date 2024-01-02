import unittest
from css_parser import *


class TestCSSParser(unittest.TestCase):
    def setUp(self):
        self.css_parser = CSSParser("")
        self.expected_tag = "test-selector"
        self.expected_prop_0 = "test-prop-0"
        self.expected_prop_1 = "test-prop-1"
        self.expected_value_0 = "test-value-0"
        self.expected_value_1 = "test-value-1"
        self.expected_pair_0 = self.expected_prop_0 + " : " + self.expected_value_0
        self.expected_pair_1 = self.expected_prop_1 + " : " + self.expected_value_1
        self.expected_body = self.expected_pair_0 + " ; " + self.expected_pair_1 + " ; "
        self.expected_css = self.expected_tag + "{ " + self.expected_body + " } "

    def test_parse(self):
        self.css_parser.s = self.expected_css

        rules = self.css_parser.parse()
        self.assertEqual(rules[0][0].tag, self.expected_tag)
        self.assertEqual(rules[0][1].get(self.expected_prop_0), self.expected_value_0)
        self.assertEqual(rules[0][1].get(self.expected_prop_1), self.expected_value_1)

    def test_selector(self):
        self.css_parser.s = self.expected_tag
        act = self.css_parser.selector()
        self.assertIsInstance(act, TagSelector)
        self.assertEqual(act.tag, self.expected_tag)

    def test_body(self):
        test = self.expected_body
        self.css_parser.s = test
        act = self.css_parser.body()
        self.assertEqual(act.get(self.expected_prop_0), self.expected_value_0)
        self.assertEqual(act.get(self.expected_prop_1), self.expected_value_1)

    def test_whitespace(self):
        self.css_parser.s = "     "
        self.css_parser.whitespace()
        self.assertEqual(self.css_parser.i, 5)

    def test_word(self):
        self.css_parser.s = self.expected_prop_0
        self.assertEqual(self.css_parser.word(), self.expected_prop_0)
        self.assertEqual(self.css_parser.i, 11)

    def test_word_exception(self):
        wrong_input = " testWord"
        self.css_parser.s = wrong_input
        with self.assertRaises(Exception, msg="Parsing error"):
            self.css_parser.word()

    def test_literal(self):
        exp = "{testWord"
        self.css_parser.s = exp
        self.css_parser.literal("{")
        self.assertEqual(self.css_parser.i, 1)

    def test_literal_exception(self):
        exp = "testWord"
        self.css_parser.s = exp
        with self.assertRaises(Exception, msg="Parsing error"):
            self.css_parser.literal("{")

    def test_pair(self):
        self.css_parser.s = self.expected_pair_0
        prop, val = self.css_parser.pair()
        self.assertEqual(prop, self.expected_prop_0)
        self.assertEqual(val, self.expected_value_0)

    def test_ignore_until(self):
        test_case = self.expected_css
        self.css_parser.s = test_case
        self.assertEqual(self.css_parser.ignore_until(["}"]), "}")
        self.assertEqual(self.css_parser.i, len(test_case) - 2)

    def test_ignore_until_not_included(self):
        test_case = "{" + self.expected_pair_0
        self.css_parser.s = test_case
        self.assertEqual(self.css_parser.ignore_until(["}"]), None)
        self.assertEqual(self.css_parser.i, len(test_case))


class TestTagSelector(unittest.TestCase):
    def test_matches(self):
        test_tag = "test_tag"
        different_tag = "different_tag"
        tag_selector = TagSelector(tag=test_tag)
        self.assertTrue(
            tag_selector.matches(Element(tag=test_tag, attribute=None, parent=None))
        )
        self.assertFalse(
            tag_selector.matches(
                Element(tag=different_tag, attribute=None, parent=None)
            )
        )


class TestDescendantSelector(unittest.TestCase):
    def test_matches(self):
        test_tag = "test_tag"
        different_tag = "different_tag"

        # descendant の tag と node.tag が一致しなければ、False
        descendant_selector = DescendantSelector(
            ancestor=None, descendant=TagSelector(tag=different_tag)
        )
        self.assertFalse(
            descendant_selector.matches(
                Element(tag=test_tag, attribute=None, parent=None)
            )
        )

        # node.parent が存在しなければ、False
        descendant_selector = DescendantSelector(
            ancestor=None, descendant=TagSelector(tag=test_tag)
        )
        self.assertFalse(
            descendant_selector.matches(
                Element(tag=test_tag, attribute=None, parent=None)
            )
        )

        # ancestor の tag と node.parent.tag が一致すれば、True
        test_ancestor = TagSelector(tag=test_tag)
        test_descendant = TagSelector(tag=test_tag)
        descendant_selector = DescendantSelector(
            ancestor=test_ancestor, descendant=test_descendant
        )
        parent_node = Element(tag=test_tag, attribute=None, parent=None)
        test_node = Element(tag=test_tag, attribute=None, parent=parent_node)
        self.assertTrue(descendant_selector.matches(test_node))
