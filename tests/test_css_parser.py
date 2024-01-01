import unittest
from css_parser import *


class TestCSSParser(unittest.TestCase):
    def setUp(self):
        self.pairs = CSSParser("")

    def test_body(self):
        test = "test-prop1:test-value1;test-prop2:test-value2;"
        self.pairs.s = test
        act = self.pairs.body()
        self.assertEqual(act.get("test-prop1"), "test-value1")
        self.assertEqual(act.get("test-prop2"), "test-value2")

    def test_whitespace(self):
        self.pairs.s = "     "
        self.pairs.whitespace()
        self.assertEqual(self.pairs.i, 5)

    def test_word(self):
        exp = "testWord"
        self.pairs.s = exp
        self.assertEqual(self.pairs.word(), exp)
        self.assertEqual(self.pairs.i, 8)

    def test_word_exception(self):
        wrong_input = " testWord"
        self.pairs.s = wrong_input
        with self.assertRaises(Exception, msg="Parsing error"):
            self.pairs.word()

    def test_literal(self):
        exp = "{testWord"
        self.pairs.s = exp
        self.pairs.literal("{")
        self.assertEqual(self.pairs.i, 1)

    def test_literal_exception(self):
        exp = "testWord"
        self.pairs.s = exp
        with self.assertRaises(Exception, msg="Parsing error"):
            self.pairs.literal("{")

    def test_pair(self):
        test = "test-prop:test-value"
        exp_prop = "test-prop"
        exp_val = "test-value"
        self.pairs.s = test
        prop, val = self.pairs.pair()
        self.assertEqual(prop, exp_prop)
        self.assertEqual(val, exp_val)

    def test_ignore_until(self):
        test = "{test-test:test}"
        self.pairs.s = test
        self.assertEqual(self.pairs.ignore_until(["}"]), "}")
        self.assertEqual(self.pairs.i, len(test) - 1)

    def test_ignore_until_not_included(self):
        test = "{test-test:test"
        self.pairs.s = test
        self.assertEqual(self.pairs.ignore_until(["}"]), None)
        self.assertEqual(self.pairs.i, len(test))
