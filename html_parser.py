from typing import List, Tuple, Dict

class Text:
        def __init__(self, text, parent) -> None:
            self.text = text
            self.parent = parent
            self.children = []
        def __repr__(self) -> str:
            return repr(self.text)
        
class Element:
    def __init__(self, tag, attribute, parent) -> None:
        self.tag = tag
        self.attribute = attribute
        self.parent = parent
        self.children = []
    
    def __repr__(self) -> str:
        return "<" + self.tag + ">"
    
class HTMLParser:
    def __init__(self, body) -> None:
        self.body = body
        self.unfinished = []
        self.SELF_CLOSING_TAGS = [
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
            "area/", "base/", "br/", "col/", "embed/", "hr/", "img/", "input/",
            "link/", "meta/", "param/", "source/", "track/", "wbr/",
        ]
        
    def parse(self) -> List[Element]:
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
    
    def add_text(self, text:str):
        parent = self.unfinished[-1] if self.unfinished else None # 最初のノードはエッジケース
        node = Text(text, parent)
        parent.children.append(node)
        
    def add_tag(self, tag:str):
        tag, attribute = self.get_attribute(tag)
        
        # doctype や　コメントアウトは無視する
        if tag.startswith("!"): return
        
        # void要素
        if tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1] if self.unfinished else None # 最初のノードはエッジケース
            node = Element(tag, attribute, parent)
            parent.children.append(node)
        elif tag.startswith("/"):
            # 最後のノードもエッジケースとして処理
            if len(self.unfinished) == 1:
                return
            # タグを閉じてノード完成
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        else:
            # 新規タグノードを作成し、未完ノードリストに追加する
            parent = self.unfinished[-1] if self.unfinished else None # 最初のノードはエッジケース
            node = Element(tag, attribute, parent)
            self.unfinished.append(node)

    def get_attribute(self, text:str) -> Tuple[str, Dict[str, str]]:
        """タグ要素の属性と属性値をパース
        Args:
            text (str): < と > の中身の文字列
        """
        parts = text.split()
        tag = parts[0].lower()
        attribute = {}
        for _attribute in parts[1:]:
            if "=" in _attribute:
                key, value = _attribute.split("=", 1)
                # value に引用符が付いている場合、引用符をストリップする
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]
                attribute[key.lower()] = value
            else:
                # 属性に=属性値が指定されていない場合、デフォルト値を設定
                # デフォルト値は空の文字列
                attribute[_attribute.lower()] = ""
            
        return tag, attribute
    
    def close_unfinished_node(self) -> Element:
        """
        閉じていない未完のタグノードを閉じればツリーの完成
        unfinishedの先頭がツリーの頂点
        """
        if len(self.unfinished) == 0:
            self.add_tag("html")
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()