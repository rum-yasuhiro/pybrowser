from layout import Text, Tag

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
                    token_list.append(Text(text))
                text = ""
            elif c == ">":
                in_tag = False
                token_list.append(Tag(text))
                text = ""
            else:
                text += c
        if not in_tag and text:
            token_list.append(Text(text))
        return token_list