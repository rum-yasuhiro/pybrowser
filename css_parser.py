from html_parser import Element


def style(dom_node):
    dom_node.style = {}
    if isinstance(dom_node, Element) and "style" in dom_node.attribute:
        pairs = CSSParser(dom_node.attribute["style"]).body()
        for property, value in pairs.items():
            dom_node.style[property] = value

    for child in dom_node.children:
        style(child)


class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def body(self):
        pairs = {}
        while self.i < len(self.s):
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                """
                パースエラーを全て無視することでデバッグしづらくなるが、
                このブラウザが対応していない CSS でも最低限ページを表示できる
                """
                why = self.ignore_until([";"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break

        return pairs

    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start : self.i]

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1

    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return prop.casefold(), val

    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None
