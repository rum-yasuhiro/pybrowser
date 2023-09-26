class HTMLParser:
    def __init__(self, body) -> None:
        self.body = body
        self.unfinished = []
        
    def parse(self):
        token_list = []
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text:
                    token_list.append(Text(text, parent=None))
                text = ""
            elif c == ">":
                in_tag = False
                token_list.append(Element(text, parent=None))
                text = ""
            else:
                text += c
        if not in_tag and text:
            token_list.append(Text(text, parent=None))
        return token_list
    
class Text:
        def __init__(self, text, parent) -> None:
            self.text = text
            self.parent = parent
            self.child = []
        
class Element:
    def __init__(self, tag, parent) -> None:
        self.tag = tag
        self.parent = parent
        self.child = []