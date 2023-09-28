class HTMLParser:
    def __init__(self, body) -> None:
        self.body = body
        self.unfinished = []
    
    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                text = text.replace("\n", "") # 改行コードは飛ばす
                text = text.strip() # 空白のみのテキストを除去
                if text: 
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(tag=text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.add_text(text=text)
        return self.close_unfinished_node()
    
    def add_text(self, text):
        parent = self.unfinished[-1] if self.unfinished else None # 最初のノードはエッジケース
        node = Text(text, parent)
        parent.child.append(node)
        
    def add_tag(self, tag):
        # タグの開閉で場合分け
        if tag.endswith("/"):
            parent = self.unfinished[-1] if self.unfinished else None # 最初のノードはエッジケース
            node = Element(tag, parent)
            parent.child.append(node)
        elif tag.startswith("/"):
            # 最後のノードもエッジケースとして処理
            if len(self.unfinished) == 1:
                return
            # タグを閉じてノード完成
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.child.append(node)
        else:
            # 新規タグノードを作成し、未完ノードリストに追加する
            parent = self.unfinished[-1] if self.unfinished else None # 最初のノードはエッジケース
            node = Element(tag, parent)
            self.unfinished.append(node)

    def close_unfinished_node(self):
        """
        閉じていない未完のタグノードを閉じればツリーの完成
        unfinishedの先頭がツリーの頂点
        """
        if len(self.unfinished) == 0:
            self.add_tag("html")
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.child.append(node)
        return self.unfinished.pop()
        
class Text:
        def __init__(self, text, parent) -> None:
            self.text = text
            self.parent = parent
            self.child = []
        def __repr__(self) -> str:
            return repr(self.text)
        
class Element:
    def __init__(self, tag, parent) -> None:
        self.tag = tag
        self.parent = parent
        self.child = []
    
    def __repr__(self) -> str:
        return "<" + self.tag + ">"