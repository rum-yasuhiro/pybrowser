from html_parser import Element


def style(dom_node, rules: list):
    dom_node.style = {}
    # CSS
    for selector, body in rules:
        if not selector.matches(dom_node):
            continue
        for property, value in body.items():
            dom_node.style[property] = value

    # HTML の style 要素
    if isinstance(dom_node, Element) and "style" in dom_node.attribute:
        pairs = CSSParser(dom_node.attribute["style"]).body()
        for property, value in pairs.items():
            dom_node.style[property] = value

    for child in dom_node.children:
        style(child, rules)


class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def parse(self):
        rules = []
        while self.i < len(self.s):
            # 解析エラーの場合、そのルールごとスキップ
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules

    def selector(self):
        out = TagSelector(self.word().casefold())
        self.whitespace()
        while self.i < len(self.s) and self.s[self.i] != "{":
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out

    def body(self):
        pairs = {}
        # 中括弧閉じ }が来たら終了
        while self.i < len(self.s) and self.s[self.i] != "}":
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
                why = self.ignore_until([";", "}"])
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


class TagSelector:
    def __init__(self, tag) -> None:
        self.tag = tag

    def matches(self, node) -> bool:
        return isinstance(node, Element) and self.tag == node.tag


class DescendantSelector:
    def __init__(self, ancestor, descendant) -> None:
        self.ancestor = ancestor
        self.descendant = descendant

    def matches(self, node) -> bool:
        if not self.descendant.matches(node):
            return False
        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
        return False
